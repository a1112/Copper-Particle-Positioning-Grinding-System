from __future__ import annotations
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Any, Dict, List
from threading import Lock
import asyncio

from app.ui.image_provider import CameraImageProvider
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


def create_app(provider: CameraImageProvider, orch: Orchestrator, motion: IMotionController, spindle: ISpindle | None = None, io: IIO | None = None) -> FastAPI:
    app = FastAPI(title="CopperSystem API")
    lock = Lock()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/image.png")
    async def image_png():
        # Encode QImage to PNG without requiring QPixmap/QGuiApplication
        from PySide6.QtGui import QImage
        from PySide6.QtCore import QByteArray, QBuffer
        with provider._lock:  # type: ignore[attr-defined]
            img = provider._img  # type: ignore[attr-defined]
            if img is None:
                image = QImage(640, 360, QImage.Format_RGB888)
                image.fill(0x202020)
                qba = QByteArray()
                buf = QBuffer(qba)
                buf.open(QBuffer.WriteOnly)
                image.save(buf, 'PNG')
                return Response(content=bytes(qba), media_type='image/png')
            else:
                qba = QByteArray()
                buf = QBuffer(qba)
                buf.open(QBuffer.WriteOnly)
                img.save(buf, 'PNG')
                return Response(content=bytes(qba), media_type='image/png')

    @app.get("/status")
    async def status():
        pos = motion.status() if hasattr(motion, 'status') else (0, 0, 0, 0)
        st = getattr(orch.sm, 'state', None)
        state = st.name if st else 'UNKNOWN'
        rpm = spindle.rpm_actual() if spindle else 0
        return {
            "state": state,
            "position": {
                "x": pos[0], "y": pos[1], "z": pos[2], "theta": pos[3]
            },
            "spindle_rpm": rpm
        }

    @app.post("/run/start")
    async def run_start():
        # Placeholder: flip to READY
        orch.sm.state = getattr(orch.sm, 'state').READY  # type: ignore
        return {"ok": True}

    @app.post("/run/stop")
    async def run_stop():
        orch.sm.state = getattr(orch.sm, 'state').IDLE  # type: ignore
        return {"ok": True}

    @app.post("/motion/set_speed")
    async def motion_set_speed(body: MotionSpeed):
        if hasattr(motion, 'set_speed'):
            motion.set_speed(body.v_fast, body.v_work)
        return {"ok": True}

    @app.post("/motion/jog")
    async def motion_jog(body: JogCmd):
        if hasattr(motion, 'jog'):
            motion.jog(body.axis, body.direction, body.speed)
        return {"ok": True}

    @app.post("/motion/home")
    async def motion_home():
        if hasattr(motion, 'home'):
            motion.home()
        return {"ok": True}

    @app.post("/motion/set_work_origin")
    async def motion_set_work_origin():
        if hasattr(motion, 'set_work_origin'):
            motion.set_work_origin()
        return {"ok": True}

    # WebSocket for status push (simple ticker)
    @app.websocket("/ws")
    async def ws_status(ws: WebSocket):
        await ws.accept()
        try:
            while True:
                s = await status()
                await ws.send_json(s)
                await asyncio.sleep(0.5)
        except WebSocketDisconnect:
            return

    # Launch UI process on demand
    from typing import Optional
    import subprocess, sys, os
    ui_proc: Optional[subprocess.Popen] = None

    @app.post("/ui/start")
    async def ui_start():
        nonlocal ui_proc
        with lock:
            if ui_proc and ui_proc.poll() is None:
                return {"ok": True, "running": True}
            # Run the UI launcher as a separate process
            env = os.environ.copy()
            cmd = [sys.executable, "-m", "app.ui.main"]
            try:
                ui_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"ok": True, "running": True}
            except Exception as e:
                return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    return app
