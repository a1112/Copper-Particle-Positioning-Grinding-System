from __future__ import annotations

import asyncio
from threading import Lock

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app.diagnostics.logging import get_logger
from app.api.endpoints import mount_ws
from app.server.utils.logs import get_buffer, attach_root_handler
from app.db.base import init_db, SessionLocal
from app.db.models import TestGroup, TestImage
from app.process.orchestrator import Orchestrator
from app.devices.motion_base import IMotionController
from app.devices.spindle_base import ISpindle
from app.devices.io_base import IIO


class MotionSpeed(BaseModel):
    v_fast: float
    v_work: float


class JogCmd(BaseModel):
    axis: str
    direction: int
    speed: float = 10.0


class GroupCreate(BaseModel):
    serial: str
    note: str | None = None


    @app.get("/status")
    async def status():
        pos = motion.status() if hasattr(motion, 'status') else (0, 0, 0, 0)
        st = getattr(orch.sm, 'state', None)
        state = st.name if st else 'UNKNOWN'
        if spindle:
            try:
                rpm = float(spindle.rpm_actual())
            except Exception:
                rpm = 0.0
            base_torque = max(0.0, min(2.0, rpm / 6000.0 * 1.2))
            torque = base_torque + (random.random() - 0.5) * 0.05
        else:
            t = time.monotonic() - _sim_t0
            rpm = 1500.0 + 600.0 * math.sin(2.0 * math.pi * 0.15 * t) + 120.0 * math.sin(2.0 * math.pi * 1.1 * t)
            torque = 0.6 + 0.25 * math.sin(2.0 * math.pi * 0.22 * t + 1.3) + 0.04 * math.sin(2.0 * math.pi * 1.8 * t)
            rpm = max(0.0, rpm)
            torque = max(0.0, torque)
        from app.server.CONFIG import DEBUG as _DBG
        return {
            "state": state,
            "position": {"x": pos[0], "y": pos[1], "z": pos[2], "theta": pos[3]},
            "spindle_rpm": int(rpm),
            "spindle_torque": round(torque, 3),
            "seriesA": rpm,
            "seriesB": torque,
            "debug": bool(_DBG),
        }# Test images support

    # Simple run controls (placeholders)
    @app.post("/run/start")
    async def run_start():
        orch.sm.state = getattr(orch.sm, 'state').READY  # type: ignore
        return {"ok": True}

    @app.post("/run/stop")
    async def run_stop():
        orch.sm.state = getattr(orch.sm, 'state').IDLE  # type: ignore
        return {"ok": True}


    # Mount WebSocket endpoints via ws module (centralized implementation)
    mount_ws(app, status, logger)

    _removed_app = FastAPI()

    # WebSocket for periodic status push
    @_removed_app.websocket("/ws") # 修改为 /ws/statu
    async def ws_status(ws: WebSocket):
        await ws.accept()
        try:
            try:
                logger.info("WS connected endpoint=/ws client=%s", getattr(ws, "client", None))
            except Exception:
                pass
            while True:
                s = await status()
                await ws.send_json(s)
                await asyncio.sleep(0.5)
        except WebSocketDisconnect:
            try:
                logger.info("WS disconnected endpoint=/ws client=%s", getattr(ws, "client", None))
            except Exception:
                pass
            return

    # Simple code execution WebSocket (demo): periodically streams a program snapshot and running index
    @_removed_app.websocket("/ws/code")
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

    # Simple logs WebSocket: send recent history and periodic heartbeats
    attach_root_handler()
    _log_buffer = get_buffer()
    try:
        logger.info("Log bus attached; history size=%d", getattr(_log_buffer, 'maxlen', 0) or 0)
    except Exception:
        pass









