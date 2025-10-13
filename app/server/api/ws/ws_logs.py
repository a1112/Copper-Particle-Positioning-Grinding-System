import asyncio

from fastapi.logger import logger
from starlette.websockets import WebSocket, WebSocketDisconnect
from ..api_core import app

@_removed_app.websocket("/ws/logs")
async def ws_logs(ws: WebSocket):
    await ws.accept()
    try:
        logger.info("WS connected endpoint=/ws/logs client=%s", getattr(ws, "client", None))
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
            logger.info("WS disconnected endpoint=/ws/logs client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return
