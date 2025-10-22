from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import Body, HTTPException

from ..api_core import cutting_router as router
from app.server.data import get_backend


def _raise_override_not_supported() -> HTTPException:
    return HTTPException(status_code=400, detail="Cutting overrides are not supported by the current backend")


@router.get("/cutting")
async def get_cutting_snapshot() -> Dict[str, Any]:
    backend = get_backend()
    try:
        snapshot = await backend.fetch_cutting()
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc) or "Cutting snapshot not supported") from exc
    return snapshot.to_dict()


@router.post("/cutting/test_payload")
async def apply_cutting_test_payload(
    payload: Dict[str, Any] = Body(...),
    merge: bool = False,
) -> Dict[str, Any]:
    backend = get_backend()
    apply_override = getattr(backend, "apply_cutting_override", None)
    if apply_override is None:
        raise _raise_override_not_supported()
    try:
        overrides = await apply_override(payload, merge=merge)
    except NotImplementedError as exc:
        raise _raise_override_not_supported() from exc
    return {"overrides": overrides, "merge": merge}


@router.get("/cutting/test_payload")
async def read_cutting_test_payload() -> Dict[str, Any]:
    backend = get_backend()
    getter = getattr(backend, "get_cutting_override", None)
    if getter is None:
        raise _raise_override_not_supported()
    try:
        overrides = await getter()
    except NotImplementedError as exc:
        raise _raise_override_not_supported() from exc
    return overrides


@router.delete("/cutting/test_payload")
async def clear_cutting_test_payload(keys: Optional[str] = None) -> Dict[str, Any]:
    backend = get_backend()
    clearer = getattr(backend, "clear_cutting_override", None)
    if clearer is None:
        raise _raise_override_not_supported()

    key_list: Optional[List[str]] = None
    if keys:
        key_list = [item.strip() for item in keys.split(",") if item.strip()]
    try:
        remaining = await clearer(key_list if key_list else None)
    except NotImplementedError as exc:
        raise _raise_override_not_supported() from exc

    cleared = key_list or ["*"]
    return {"cleared": cleared, "remaining": remaining}
