import asyncio
import time
from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi.logger import logger
from ..api_core import ws_router


@ws_router.websocket("/ws/cutting")
async def ws_cutting(ws: WebSocket):
    await ws.accept()
    try:
        logger.info("WS connected endpoint=/ws/cutting client=%s", getattr(ws, "client", None))
    except Exception:
        pass
    t0 = time.monotonic()
    cut_depth_target = 0.8  # mm
    removal_expected = 120.0  # mm^3 (demo)
    torque_max_seen = 0.0
    try:
        while True:
            t = time.monotonic() - t0
            # Simulate feed rate (mm/s) and downfeed current (mm)
            import math, random
            feed_rate = 20.0 + 5.0 * math.sin(t * 0.5)
            downfeed_current = min(cut_depth_target, max(0.0, cut_depth_target * (t / 10.0)))
            # Simulate material removal (mm^3) proportional to feed and time
            removal_current = min(removal_expected, max(0.0, removal_expected * (t / 20.0)))
            # Simulate torque
            torque = 0.3 + 0.2 * abs(math.sin(t * 0.8)) + 0.05 * random.random()
            torque_max_seen = max(torque_max_seen, torque)
            frame = {
                "ts": time.time(),
                "feed_rate": round(feed_rate, 3),           # ????/???? (mm/s)
                "downfeed_target": round(cut_depth_target, 3),
                "downfeed_current": round(downfeed_current, 3),
                "removal_current": round(removal_current, 3),
                "removal_expected": round(removal_expected, 3),
                "torque_max": round(torque_max_seen, 3),
                "torque": round(torque, 3),
                "elapsed_sec": round(t, 2),
            }
            try:
                await ws.send_json(frame)
            except RuntimeError:
                await asyncio.sleep(0.5)
                continue
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        try:
            logger.info("WS disconnected endpoint=/ws/cutting client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return
