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
    # Demo program lines
    demo_lines = [
        "FastMove SX 0 SY 0 SZ 10 EX 10 EY 10 EZ 10",
        "FastCut  SX 10 SY 10 SZ 10 EX 20 EY 10 EZ  8 V 50 R 1000",
        "SetDO 1,2,3",
        "FastMove SX 20 SY 10 SZ  8 EX  0 EY  0 EZ 10",
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