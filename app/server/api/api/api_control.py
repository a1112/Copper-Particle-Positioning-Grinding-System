from __future__ import annotations

from starlette.responses import JSONResponse
from ..api_core import control_router as router
import logging

log = logging.getLogger("app.control")

try:
    from app.server.utils.logs import push as log_push
except Exception:
    def log_push(level: str, name: str, msg: str) -> None:
        pass


@router.post("/control/estop")
async def control_estop():
    try:
        log.warning("E-STOP triggered by API")
        log_push("WARN", "control", "E-STOP triggered")
        # If motion supports a stop/estop in future, call it here
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@router.post("/control/reset")
async def control_reset():
    try:
        import motion  # provided by run_api injection
        if hasattr(motion, "home"):
            motion.home()
        log_push("INFO", "control", "Reset requested -> home")
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@router.post("/control/stop")
async def control_stop():
    try:
        # Placeholder soft-stop; integrate with orchestrator/motion when available
        log_push("INFO", "control", "Soft stop requested")
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
