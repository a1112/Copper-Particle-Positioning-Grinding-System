import asyncio
import time
from typing import List, Dict, Any

from fastapi.logger import logger
from starlette.websockets import WebSocket, WebSocketDisconnect
from ..api_core import ws_router
from app.server.utils import logs as logbuf


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

        # Send current history snapshot
        history: List[Dict[str, Any]] = logbuf.as_list()
        await ws.send_json({"type": "history", "items": history})
        last_len = len(history)
        idle_ticks = 0

        while True:
            buf_list = logbuf.as_list()
            if len(buf_list) < last_len:
                # Buffer rotated/truncated; resend full snapshot
                await ws.send_json({"type": "history", "items": buf_list})
                last_len = len(buf_list)
                idle_ticks = 0
            elif len(buf_list) > last_len:
                # Send newly appended items
                for item in buf_list[last_len:]:
                    await ws.send_json({"type": "append", "item": item})
                idle_ticks = 0
                last_len = len(buf_list)
            else:
                # No new logs; emit a lightweight heartbeat periodically
                idle_ticks += 1
                if idle_ticks >= 6:  # ~3s at 0.5s interval
                    hb = {"ts": time.time(), "level": "INFO", "name": "app", "msg": "heartbeat"}
                    await ws.send_json({"type": "append", "item": hb})
                    idle_ticks = 0

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        try:
            logger.info("WS disconnected endpoint=/ws/logs client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return
