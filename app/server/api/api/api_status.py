from typing import Any, Dict, List, Optional

from fastapi import Body, HTTPException

from ..api_core import status_router as router
from app.domain.status import get_status_provider
from app.server.data import get_backend


@router.get("/status")
async def status():
    backend = get_backend()
    status_model = await backend.fetch_status()
    payload = status_model.to_dict()
    try:
        from app.config import DEBUG as _DBG  # type: ignore
        payload["debug"] = bool(_DBG)
    except Exception:
        pass
    return payload


@router.post("/status/test_payload")
async def apply_status_test_payload(
    payload: Dict[str, Any] = Body(...),
    merge: bool = False,
) -> Dict[str, Any]:
    """Apply a manual status payload so simulators can mimic production data."""
    provider = get_status_provider()
    apply_fn = getattr(provider, "apply_manual_snapshot", None)
    if apply_fn is None:
        raise HTTPException(status_code=400, detail="Status provider does not support manual overrides")
    overrides = apply_fn(payload, reset=not merge)
    return {"overrides": overrides, "merge": merge}


@router.delete("/status/test_payload")
async def clear_status_test_payload(keys: Optional[str] = None) -> Dict[str, Any]:
    """Clear manual overrides entirely or drop a subset of keys."""
    provider = get_status_provider()
    clear_fn = getattr(provider, "clear_manual_snapshot", None)
    if clear_fn is None:
        raise HTTPException(status_code=400, detail="Status provider does not support manual overrides")
    cleared_keys: List[str] = []
    if keys:
        cleared_keys = [item.strip() for item in keys.split(",") if item.strip()]
        if cleared_keys:
            clear_fn(*cleared_keys)
    if not cleared_keys:
        clear_fn()
        cleared_keys = ["*"]
    return {"cleared": cleared_keys}


@router.get("/status/test_payload")
async def read_status_test_payload() -> Dict[str, Any]:
    """Expose current manual overrides for diagnostics."""
    provider = get_status_provider()
    snapshot_fn = getattr(provider, "get_manual_snapshot", None)
    if snapshot_fn is None:
        raise HTTPException(status_code=400, detail="Status provider does not support manual overrides")
    return snapshot_fn()



@router.get("/delay")
async def get_delay():
    return 0


@router.get("/health")
async def health():
    return {"status": "ok"}
