import asyncio

from fastapi.logger import logger
from starlette.websockets import WebSocket, WebSocketDisconnect
from ..api_core import ws_router
import logging

log =logging.getLogger("app.ws")

@ws_router.websocket("/ws/status")
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