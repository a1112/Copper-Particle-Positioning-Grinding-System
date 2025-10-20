from __future__ import annotations

import logging

from starlette.responses import JSONResponse

from ..api_core import control_router as router
from app.server.data import get_backend
from app.server.models import ControlCommand

log = logging.getLogger("app.control")

@router.post("/control/estop")
async def control_estop():
    backend = get_backend()
    result = await backend.execute_control(ControlCommand.create("estop"))
    if result.ok:
        log.warning("E-STOP triggered by API")
        return result.to_dict()
    return JSONResponse(status_code=500, content=result.to_dict())


@router.post("/control/reset")
async def control_reset():
    backend = get_backend()
    result = await backend.execute_control(ControlCommand.create("reset"))
    if result.ok:
        return result.to_dict()
    return JSONResponse(status_code=500, content=result.to_dict())


@router.post("/control/stop")
async def control_stop():
    backend = get_backend()
    result = await backend.execute_control(ControlCommand.create("stop"))
    if result.ok:
        return result.to_dict()
    return JSONResponse(status_code=500, content=result.to_dict())
