from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import HTTPException
from starlette.responses import JSONResponse

from ..api_core import control_router as router
from ..api_models import ControlCommandPayload
from app.server.data import get_backend
from app.server.models import ControlCommand

log = logging.getLogger("app.control")


def _snapshot_params(params: Dict[str, Any]) -> Dict[str, Any]:
    # avoid mutating the original mapping while providing a shallow preview for logs
    return dict(params)


@router.post("/control")
async def control_entry(payload: ControlCommandPayload):
    action = payload.action.strip()
    if not action:
        log.warning("Control request rejected: missing action")
        raise HTTPException(status_code=400, detail="Control action is required")

    params = payload.params or {}
    log.info("Control request received action=%s params=%s", action, _snapshot_params(params))

    backend = get_backend()
    result = await backend.execute_control(ControlCommand.create(action, params))
    response_payload = result.to_dict()
    response_payload.setdefault("action", action)
    if result.ok:
        log.info(
            "Control action succeeded action=%s message=%s",
            action,
            response_payload.get("message", ""),
        )
        return response_payload

    log.warning(
        "Control action failed action=%s message=%s",
        action,
        response_payload.get("message", ""),
    )
    return JSONResponse(status_code=500, content=response_payload)
