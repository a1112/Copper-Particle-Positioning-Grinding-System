from __future__ import annotations

"""
Factory for building the FastAPI app used by the UI and smoke tests.

Bridges the current server implementation under `app.server.api` by:
- Exposing legacy module aliases expected by route modules (CONFIG, db, motion)
- Importing HTTP/WS route modules to populate routers
- Attaching routers onto the FastAPI app
- Injecting runtime singletons (e.g., image provider) where needed
"""

import sys
from types import ModuleType
from typing import Any


def _ensure_module_alias(name: str, module: Any) -> None:
    if name not in sys.modules:
        sys.modules[name] = module  # type: ignore[assignment]


def _wrap_motion_module(controller: Any) -> ModuleType:
    proxy = ModuleType("motion")
    for attr in (
        "set_speed",
        "jog",
        "home",
        "set_work_origin",
        "status",
        "move_abs",
        "wait_done",
    ):
        if hasattr(controller, attr):
            setattr(proxy, attr, getattr(controller, attr))
    proxy.controller = controller  # type: ignore[attr-defined]
    return proxy


def create_app(provider: Any, orch: Any, motion: Any):
    """Create and return the FastAPI app, wiring required singletons.

    Parameters
    - provider: CameraImageProvider (or compatible) used by /image.png
    - orch:     Orchestrator instance (not directly required by current routes)
    - motion:   Motion controller/sim; exposed via a lightweight module proxy
    """
    # Import core app/routers
    from app.server.api import api_core as core
    from app.server import CONFIG as real_config

    # Optional database package; route files expect `db` alias to exist
    try:
        import app.db as app_db  # type: ignore
    except Exception:
        app_db = None

    # Expose legacy module names used by route files
    _ensure_module_alias("CONFIG", real_config)
    if app_db is not None:
        _ensure_module_alias("db", app_db)

    # Expose a motion proxy as a module for routes/services which import `motion`
    sys.modules["motion"] = _wrap_motion_module(motion)

    # Import HTTP route modules so their routers get populated
    from app.server.api.api import (
        api_config,
        api_control,
        api_image,
        api_motion,
        api_path,
        api_status,
        api_test,
    )  # noqa: F401
    from app.server.api.ws import ws_status  # noqa: F401

    # Inject provider into the image endpoint module when available
    try:
        setattr(api_image, "provider", provider)  # type: ignore[name-defined]
    except Exception:
        pass

    # ws_status needs a status_fn thunk
    async def _status_fn():
        try:
            return await api_status.status()  # type: ignore[attr-defined]
        except Exception:
            return {
                "state": "ERROR",
                "position": {},
                "spindle_rpm": 0,
                "spindle_torque": 0.0,
                "seriesA": 0,
                "seriesB": 0,
            }

    try:
        setattr(ws_status, "status_fn", _status_fn)  # type: ignore[name-defined]
    except Exception:
        pass

    # Attach routers to the FastAPI app (idempotent)
    core.include_router()
    return core.app

