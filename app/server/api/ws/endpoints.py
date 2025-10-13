from __future__ import annotations

import asyncio
import logging
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.api.utils.logs import get_buffer, attach_root_handler


StatusFn = Callable[[], Awaitable[dict]]


def mount_ws(app: FastAPI, status_fn: StatusFn, logger: logging.Logger | None = None) -> None:
    """Mount all WebSocket endpoints under a unified module.

    - /ws:      periodic status push (uses provided `status_fn`)
    - /ws/code: demo program streaming (mock)
    - /ws/logs: log history + live append from unified log bus
    """
    log = logger or logging.getLogger("app.ws")

    # Ensure log bus is attached once
    attach_root_handler()
    _log_buffer = get_buffer()

    @app.websocket("/ws")
    async def ws_status(ws: WebSocket):
        await ws.accept()
        try:
            try:
                log.info("WS connected endpoint=/ws client=%s", getattr(ws, "client", None))
            except Exception:
                pass
            while True:
                s = await status_fn()
                await ws.send_json(s)
                await asyncio.sleep(0.5)
        except WebSocketDisconnect:
            try:
                log.info("WS disconnected endpoint=/ws client=%s", getattr(ws, "client", None))
            except Exception:
                pass
            return

    @app.websocket("/ws/code")
    async def ws_code(ws: WebSocket):
        await ws.accept()
        try:
            log.info("WS connected endpoint=/ws/code client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        demo_lines = [
            "FastMove SX 0 SY 0 SZ 10 EX 10 EY 10 EZ 10",
            "FastCut  SX 10 SY 10 SZ 10 EX 20 EY 10 EZ  8 V 50 R 1000",
            "SetDO 1,2,3",
            "FastMove SX 20 SY 10 SZ  8 EX  0 EY  0 EZ 10",
        ]
        await ws.send_json({"type": "program", "lines": demo_lines})
        idx = -1
        try:
            while True:
                for i in range(len(demo_lines)):
                    idx = i
                    await ws.send_json({"type": "state", "state": "RUNNING", "current": idx})
                    await asyncio.sleep(1.0)
                idx = -1
                await ws.send_json({"type": "state", "state": "IDLE", "current": idx})
                await asyncio.sleep(2.0)
        except WebSocketDisconnect:
            try:
                log.info("WS disconnected endpoint=/ws/code client=%s", getattr(ws, "client", None))
            except Exception:
                pass
            return

    @app.websocket("/ws/logs")
    async def ws_logs(ws: WebSocket):
        await ws.accept()
        try:
            log.info("WS connected endpoint=/ws/logs client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        try:
            await ws.send_json({"type": "history", "items": list(_log_buffer)})
            while True:
                item = {"ts": time.time(), "level": "INFO", "name": "app", "msg": "heartbeat"}
                _log_buffer.append(item)
                await ws.send_json({"type": "append", "item": item})
                await asyncio.sleep(3.0)
        except WebSocketDisconnect:
            try:
                log.info("WS disconnected endpoint=/ws/logs client=%s", getattr(ws, "client", None))
            except Exception:
                pass
            return
