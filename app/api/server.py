from __future__ import annotations

import asyncio
from threading import Lock
from typing import Any
from collections import deque
from collections import deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app.ui.src.image_provider import CameraImageProvider
from app.db import init_db, SessionLocal
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


def create_app(
    provider: CameraImageProvider,
    orch: Orchestrator,
    motion: IMotionController,
    spindle: ISpindle | None = None,
    io: IIO | None = None,
) -> FastAPI:
    """Create FastAPI app for headless API server."""

    app = FastAPI(title="CopperSystem API")
    lock = Lock()

    # --- Simulated telemetry clock for demo charts ---
    import time, math, random
    _sim_t0 = time.monotonic()
    # Ensure DB schema exists
    try:
        init_db()
    except Exception:
        pass

    # Test data root (groups stored as 娴嬭瘯鏂囦欢/<serial>)
    from pathlib import Path

    if Path("娴嬭瘯鏂囦欢").exists():
        _test_root = Path("娴嬭瘯鏂囦欢").resolve()
    else:
        _test_root = Path(".").resolve()
    # Absolute path to default PNG for /image.png override
    _project_root = Path(__file__).resolve().parents[2]
    _override_png = _project_root / "娴嬭瘯鏂囦欢" / "images" / "1_IMG_Texture_8Bit.png"

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/image.png")
    async def image_png():
        # If override test image exists, return its bytes
        try:
            if _override_png.exists():
                return Response(content=_override_png.read_bytes(), media_type='image/png')
        except Exception:
            pass
        # Else return current frame as PNG; gray fallback if empty
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
        from app.config import DEBUG as _DBG
        return {
            "state": state,
            "position": {"x": pos[0], "y": pos[1], "z": pos[2], "theta": pos[3]},
            "spindle_rpm": int(rpm),
            "spindle_torque": round(torque, 3),
            "seriesA": rpm,
            "seriesB": torque,
            "debug": bool(_DBG),
        }# Test images support
    @app.get("/test/images")
    async def list_test_images():
        try:
            items: list[str] = []
            for p in _test_root.rglob("*"):
                if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"):
                    rel = p.relative_to(_test_root)
                    items.append(str(rel))
            items.sort()
            return {"root": str(_test_root), "files": items}
        except Exception as e:
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    @app.post("/test/load_image")
    async def load_test_image(name: str):
        try:
            import cv2
            import numpy as np
            path = (_test_root / name).resolve()
            if not str(path).startswith(str(_test_root)):
                return JSONResponse(status_code=400, content={"ok": False, "error": "invalid name"})
            if not path.exists():
                return JSONResponse(status_code=404, content={"ok": False, "error": "not found"})
            img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            if img is None:
                return JSONResponse(status_code=415, content={"ok": False, "error": "unsupported image"})
            # Normalize to 3-channel uint8 BGR
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.ndim == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            if img.dtype != np.uint8:
                img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            provider.set_frame(img)
            return {"ok": True, "name": name}
        except Exception as e:
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    @app.post("/test/load_default")
    async def load_default():
        preferred = ["1_IMG_Texture_8Bit.png", "1_IMG_Texture_B.tif"]
        files = (await list_test_images())["files"]  # type: ignore
        choice: str | None = None
        for n in preferred:
            for f in files:
                if f.endswith("/" + n) or f == n:
                    choice = f
                    break
            if choice:
                break
        if not choice:
            choice = files[0] if files else None
        if not choice:
            return JSONResponse(status_code=404, content={"ok": False, "error": "no test images"})
        return await load_test_image(choice)

    # Groups APIs
    @app.post("/test/group/create")
    async def group_create(body: GroupCreate):
        serial = body.serial.strip()
        if not serial:
            return JSONResponse(status_code=400, content={"ok": False, "error": "serial required"})
        group_dir = (_test_root / serial)
        try:
            group_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
        db = SessionLocal()
        try:
            g = db.query(TestGroup).filter(TestGroup.serial == serial).one_or_none()
            if g is None:
                g = TestGroup(serial=serial, note=body.note)
                db.add(g)
                db.commit()
                db.refresh(g)
            else:
                if body.note and g.note != body.note:
                    g.note = body.note
                    db.commit()
            return {"ok": True, "serial": g.serial, "id": g.id}
        finally:
            db.close()

    @app.get("/test/group/list")
    async def group_list():
        db = SessionLocal()
        try:
            rows = db.query(TestGroup).order_by(TestGroup.created_at.desc()).all()
            return {"groups": [{"id": r.id, "serial": r.serial, "note": r.note, "created_at": r.created_at.isoformat()} for r in rows]}
        finally:
            db.close()

    @app.get("/test/group/{serial}/images")
    async def group_images(serial: str):
        group_dir = (_test_root / serial)
        if not group_dir.exists():
            return JSONResponse(status_code=404, content={"ok": False, "error": "group folder not found"})
        files = [p.name for p in group_dir.iterdir() if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")]
        files.sort()
        return {"root": str(group_dir), "files": files}

    @app.post("/test/group/{serial}/add_image")
    async def group_add_image(serial: str, name: str):
        src = (_test_root / name)
        if not src.exists():
            alt = Path("docs/閾滅矑瀛愰」鐩?绠楁硶/A001绮掑瓙鎵撶（/ImageSimMx") / name
            if alt.exists():
                src = alt.resolve()
        if not src.exists():
            return JSONResponse(status_code=404, content={"ok": False, "error": "source image not found"})
        dst_dir = (_test_root / serial)
        try:
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = (dst_dir / src.name)
            import shutil
            shutil.copyfile(src, dst)
        except Exception as e:
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
        db = SessionLocal()
        try:
            g = db.query(TestGroup).filter(TestGroup.serial == serial).one_or_none()
            if g is None:
                g = TestGroup(serial=serial)
                db.add(g)
                db.commit()
                db.refresh(g)
            rel = str(Path("娴嬭瘯鏂囦欢") / serial / src.name)
            ti = db.query(TestImage).filter(TestImage.group_id == g.id, TestImage.filename == src.name).one_or_none()
            if ti is None:
                ti = TestImage(group_id=g.id, filename=src.name, rel_path=rel)
                db.add(ti)
                db.commit()
            return {"ok": True, "file": src.name}
        finally:
            db.close()

    # Simple run controls (placeholders)
    @app.post("/run/start")
    async def run_start():
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

    # WebSocket for periodic status push
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

    # Simple code execution WebSocket (demo): periodically streams a program snapshot and running index
    @app.websocket("/ws/code")
    async def ws_code(ws: WebSocket):
        await ws.accept()
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
            return

    # Simple logs WebSocket: send recent history and periodic heartbeats
    _log_buffer = deque(maxlen=1000)

    @app.websocket("/ws/logs")
    async def ws_logs(ws: WebSocket):
        await ws.accept()
        try:
            await ws.send_json({"type": "history", "items": list(_log_buffer)})
            while True:
                item = {"ts": time.monotonic(), "level": "INFO", "name": "server", "msg": "heartbeat"}
                _log_buffer.append(item)
                await ws.send_json({"type": "append", "item": item})
                await asyncio.sleep(3.0)
        except WebSocketDisconnect:
            return

    # Optional: spawn UI as a child process
    from typing import Optional
    import subprocess, sys as _sys, os as _os

    ui_proc: Optional[subprocess.Popen] = None

    @app.post("/ui/start")
    async def ui_start():
        nonlocal ui_proc
        with lock:
            if ui_proc and ui_proc.poll() is None:
                return {"ok": True, "running": True}
            env = _os.environ.copy()
            cmd = [_sys.executable, "-m", "app.ui.main"]
            try:
                ui_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"ok": True, "running": True}
            except Exception as e:
                return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    return app







