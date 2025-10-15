import asyncio

from fastapi.logger import logger
from starlette.websockets import WebSocket, WebSocketDisconnect
from ..api_core import ws_router
from .code_bus import bus


@ws_router.websocket("/ws/code")
async def ws_code(ws: WebSocket):
    await ws.accept()
    try:
        logger.info("WS connected endpoint=/ws/code client=%s", getattr(ws, "client", None))
    except Exception:
        pass

    # On connect: send latest program (or a tiny placeholder)
    lines = bus.latest_program()
    if not lines:
        lines = [
            "%",
            "O1000 (Awaiting Program)",
            "G90 G21 G17",
            "G0 Z5.000",
            "M30",
        ]
    try:
        await ws.send_json({"type": "program", "lines": lines})
    except Exception:
        pass

    q = bus.subscribe()
    try:
        while True:
            msg = await q.get()
            await ws.send_json(msg)
    except WebSocketDisconnect:
        try:
            logger.info("WS disconnected endpoint=/ws/code client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return
