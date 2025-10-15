import asyncio

from fastapi.logger import logger
from starlette.websockets import WebSocket, WebSocketDisconnect
from ..api_core import ws_router

@ws_router.websocket("/ws/code")
async def ws_code(ws: WebSocket):
    await ws.accept()
    try:
        logger.info("WS connected endpoint=/ws/code client=%s", getattr(ws, "client", None))
    except Exception:
        pass
    # Demo program lines (G-code style)
    demo_lines = [
        "%",
        "O1001 (Copper Pocket Demo)",
        "G90 G54 G17",
        "G21",
        "G0 X0 Y0 Z5.000",
        "M3 S12000",
        "G1 Z0.500 F300",
        "G1 X25.000 Y0.000 F800",
        "G2 X25.000 Y25.000 I0.000 J12.500",
        "G1 X0.000 Y25.000",
        "G0 Z5.000",
        "M5",
        "M30",
    ]
    # Send snapshot once
    await ws.send_json({"type": "program", "lines": demo_lines})
    idx = -1
    try:
        while True:
            # simulate run
            for i in range(len(demo_lines)):
                idx = i
                await ws.send_json({"type": "state", "state": "RUNNING", "current": idx})
                await asyncio.sleep(1.0)
            idx = -1
            await ws.send_json({"type": "state", "state": "IDLE", "current": idx})
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        try:
            logger.info("WS disconnected endpoint=/ws/code client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return
