from __future__ import annotations

import signal
import sys
from types import ModuleType
from typing import Any

import uvicorn

import app.config as CONFIG
from app.devices.motion_base import IMotionController
from app.runtime.environment import bootstrap_environment
from app.ui.src.image_provider import CameraImageProvider
from app.server.utils.logs import attach_root_handler, push
from app.diagnostics.logging import get_logger
from app.server.api.api_core import app, include_router
from app.server.data import get_backend


def _ensure_module_alias(name: str, module: Any) -> None:
    """Expose an imported module under a legacy shorthand name if absent."""
    if name not in sys.modules:
        sys.modules[name] = module


def _wrap_motion_module(controller: IMotionController) -> ModuleType:
    """Export motion controller methods through a lightweight module proxy."""
    proxy = ModuleType("motion")
    for attr in ("set_speed", "jog", "home", "set_work_origin", "status", "move_abs", "wait_done"):
        if hasattr(controller, attr):
            setattr(proxy, attr, getattr(controller, attr))
    proxy.controller = controller  # type: ignore[attr-defined]
    return proxy


def _bootstrap_api_modules(log, orch, motion: IMotionController) -> None:
    """Eagerly import API/WS modules and inject runtime singletons they expect."""
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
    from app.server.api.api import (
        api_image,
        api_status,
        api_cutting,
        api_control,
        api_config,
        api_path,
        api_settings,
        api_tool,
        api_vision,
        api_data,
        api_test,
    )
    from app.server.api.ws import ws_code, ws_logs, ws_status, ws_tasks
    # Inject image provider if available
    include_router()

    async def _status_fn():
        try:
            backend = get_backend()
            model = await backend.fetch_status()
            return model.to_dict()
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

    mode = getattr(CONFIG, "data_mode", CONFIG.DATA_MODE)
    endpoint = getattr(CONFIG, "data_endpoint", CONFIG.DATA_ENDPOINT)
    try:
        log.info("API using data_mode=%s endpoint=%s", mode, endpoint or "N/A")
    except Exception:
        pass
    bindings, _service = bootstrap_environment(mode, endpoint=endpoint)
    motion = bindings.motion
    orch = bindings.orchestrator

    # Vision + camera setup (headless)
    vision = bindings.vision
    cam = bindings.camera
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
        _bootstrap_api_modules(log, orch, motion)
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







