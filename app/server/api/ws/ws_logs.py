from __future__ import annotations

import asyncio
import time
from typing import List, Dict, Any

from fastapi.logger import logger
from starlette.websockets import WebSocket, WebSocketDisconnect

from ..api_core import ws_router
from app.server.utils import logs


@ws_router.websocket("/ws/logs")
async def ws_logs(ws: WebSocket):
    """Stream log history first, then append new log records.

    - History: one message {"type":"history","items":[...]}
    - Incremental: {"type":"append","item": {...}}
    Falls back to periodic heartbeat when no new logs are available.
    """
    await ws.accept()
    try:
        try:
            logger.info("WS connected endpoint=/ws/logs client=%s", getattr(ws, "client", None))
        except Exception:
            pass

        history: List[Dict[str, Any]] = list(logs.as_list())
        await ws.send_json({"type": "history", "items": history})
        last_seen = history[-1] if history else None
        idle_ticks = 0

        while True:
            buf_list = list(logs.as_list())
            if not buf_list:
                if last_seen is not None:
                    await ws.send_json({"type": "history", "items": buf_list})
                    last_seen = None
                    idle_ticks = 0
            elif last_seen is None:
                await ws.send_json({"type": "history", "items": buf_list})
                last_seen = buf_list[-1]
                idle_ticks = 0
            else:
                if buf_list[-1] is last_seen:
                    # No new logs; emit a lightweight heartbeat periodically
                    idle_ticks += 1
                    if idle_ticks >= 600:  # ~3s at 0.5s interval
                        hb = {"ts": time.time(), "level": "INFO", "name": "app", "msg": "heartbeat"}
                        await ws.send_json({"type": "append", "item": hb})
                        idle_ticks = 0
                else:
                    last_index = None
                    for i, item in enumerate(buf_list):
                        if item is last_seen:
                            last_index = i
                            break
                    if last_index is None:
                        # Buffer rotated/truncated; resend full snapshot
                        await ws.send_json({"type": "history", "items": buf_list})
                    else:
                        for item in buf_list[last_index + 1 :]:
                            await ws.send_json({"type": "append", "item": item})
                    last_seen = buf_list[-1]
                    idle_ticks = 0

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        try:
            logger.info("WS disconnected endpoint=/ws/logs client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return
