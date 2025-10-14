from __future__ import annotations

import signal
import sys
from importlib import import_module
from types import ModuleType
from typing import Any, Dict

import uvicorn

from app.core.events import EventBus
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim
from app.devices.sim.motion_sim import MotionSim
from app.process.orchestrator import Orchestrator
from app.ui.src.image_provider import CameraImageProvider
from app.server.utils.logs import attach_root_handler, push
from app.diagnostics.logging import get_logger
from app.server import CONFIG
from api.api_core import app,include_router
from app.data.providers import set_provider, SimDataProvider, CommDataProvider


def _ensure_module_alias(name: str, module: Any) -> None:
    """Expose an imported module under a legacy shorthand name if absent."""
    if name not in sys.modules:
        sys.modules[name] = module


def _wrap_motion_module(controller: MotionSim) -> ModuleType:
    """Export motion controller methods through a lightweight module proxy."""
    proxy = ModuleType("motion")
    for attr in ("set_speed", "jog", "home", "set_work_origin", "status", "move_abs", "wait_done"):
        if hasattr(controller, attr):
            setattr(proxy, attr, getattr(controller, attr))
    proxy.controller = controller  # type: ignore[attr-defined]
    return proxy


def _bootstrap_api_modules(log, provider: CameraImageProvider, orch: Orchestrator, motion: MotionSim) -> None:
    """Eagerly import API/WS modules and inject runtime singletons they expect."""
    import math
    import random
    import time

    from app.server.utils.logs import get_buffer

    # Provide legacy module aliases expected by individual route modules.
    _ensure_module_alias("CONFIG", CONFIG)
    try:
        import app.db as app_db
    except Exception:
        app_db = None
    else:
        _ensure_module_alias("db", app_db)

    motion_proxy = _wrap_motion_module(motion)
    sys.modules["motion"] = motion_proxy
    from api.api import api_image,api_motion,api_status,api_test,api_control,api_config,api_path
    from api.ws import ws_code,ws_logs,ws_status
    include_router()
    # Default to simulated data provider for decoupled business logic
    try:
        set_provider(CommDataProvider() if getattr(CONFIG, 'data_mode', 'sim')=='comm' else SimDataProvider())
    except Exception:
        pass
    async def _status_fn():
        try:
            return await api_status.status()
        except Exception as exc:
            if log:
                try:
                    log.warning("Status endpoint failed: %s", exc, exc_info=False)
                except Exception:
                    pass
            return {"state": "ERROR", "position": {}, "spindle_rpm": 0, "spindle_torque": 0.0, "seriesA": 0, "seriesB": 0}

    ws_status.status_fn = _status_fn


def main() -> None:
    # Attach buffer handler before producing logs
    attach_root_handler()
    log = get_logger("cli")

    bus = EventBus()
    motion = MotionSim()
    orch = Orchestrator(bus, motion)

    # Vision + camera setup (headless)
    vision = VisionPipeline(bus)
    cam = CameraSim()
    cam.open()

    provider = CameraImageProvider()

    def on_frame(frame):
        vision.on_frame(frame)
        try:
            provider.set_frame(frame)
        except Exception:
            pass

    cam.start_stream(on_frame)

    def _stop_cam(*_):
        try:
            cam.stop_stream()
            cam.close()
        except Exception:
            pass

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _stop_cam)
        except Exception:
            pass

    try:
        _bootstrap_api_modules(log, provider, orch, motion)
    except Exception as exc:
        if log:
            try:
                log.error("Failed to bootstrap API modules: %s", exc, exc_info=False)
            except Exception:
                pass
        raise

    try:
        log.info("API starting at %s:%s", CONFIG.app_host, CONFIG.app_port)
        push("INFO", "api", f"Starting at {CONFIG.app_host}:{CONFIG.app_port}")
    except Exception:
        pass

    uvicorn.run(app, host=CONFIG.app_host, port=CONFIG.app_port, log_level=CONFIG.log_level)

    # Ensure camera stops after app exits
    _stop_cam()


if __name__ == "__main__":
    main()





