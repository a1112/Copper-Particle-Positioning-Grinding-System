from __future__ import annotations

import math
import time
from typing import Any, Dict, Optional

from fastapi import Body

from ..api_core import path_router as router

_START = time.monotonic()
_MAX_TORQUE = 0.0
_MANUAL_PAYLOAD: Dict[str, Any] = {}


def _merge_cutting_payload(base: Dict[str, Any]) -> Dict[str, Any]:
    """Overlay manual payload values onto the simulated base snapshot."""
    if not _MANUAL_PAYLOAD:
        return base
    merged = dict(base)
    for key, value in _MANUAL_PAYLOAD.items():
        merged[key] = value
    return merged


@router.get("/cutting", tags=["cutting"])
async def get_cutting_snapshot() -> Dict[str, Any]:
    """Return a simulated cutting telemetry snapshot (previously streamed via WS)."""
    global _MAX_TORQUE

    elapsed = time.monotonic() - _START
    feed_rate = 20.0 + 5.0 * math.sin(elapsed * 0.5)
    downfeed_target = 0.8
    downfeed_current = min(downfeed_target, max(0.0, downfeed_target * (elapsed / 10.0)))
    removal_expected = 120.0
    removal_current = min(removal_expected, max(0.0, removal_expected * (elapsed / 20.0)))
    torque = 0.3 + 0.2 * abs(math.sin(elapsed * 0.8)) + 0.05 * abs(math.sin(elapsed * 1.7))
    _MAX_TORQUE = max(_MAX_TORQUE, torque)

    payload: Dict[str, Any] = {
        "ts": time.time(),
        "feed_rate": round(feed_rate, 3),
        "downfeed_target": round(downfeed_target, 3),
        "downfeed_current": round(downfeed_current, 3),
        "removal_current": round(removal_current, 3),
        "removal_expected": round(removal_expected, 3),
        "torque_max": round(_MAX_TORQUE, 3),
        "torque": round(torque, 3),
        "elapsed_sec": round(elapsed, 2),
    }

    payload = _merge_cutting_payload(payload)

    # Keep torque_max consistent even when overrides are applied.
    try:
        torque_value = float(payload.get("torque", 0.0) or 0.0)
    except Exception:
        torque_value = 0.0
    try:
        torque_max_value = float(payload.get("torque_max", 0.0) or 0.0)
    except Exception:
        torque_max_value = 0.0
    payload["torque_max"] = round(max(torque_max_value, torque_value), 3)

    return payload


@router.post("/cutting/test_payload", tags=["cutting"])
async def apply_cutting_test_payload(
    payload: Dict[str, Any] = Body(...),
    merge: bool = False,
) -> Dict[str, Any]:
    """Apply manual payload values so the UI can display canned cutting telemetry."""
    global _MANUAL_PAYLOAD
    if not merge:
        _MANUAL_PAYLOAD = {}
    if payload:
        _MANUAL_PAYLOAD = {**_MANUAL_PAYLOAD, **payload}
    return {"overrides": dict(_MANUAL_PAYLOAD), "merge": merge}


@router.delete("/cutting/test_payload", tags=["cutting"])
async def clear_cutting_test_payload(keys: Optional[str] = None) -> Dict[str, Any]:
    """Clear manual overrides entirely or remove specific fields."""
    global _MANUAL_PAYLOAD, _MAX_TORQUE
    cleared_keys = []
    if keys:
        cleared_keys = [item.strip() for item in keys.split(",") if item.strip()]
        for key in cleared_keys:
            _MANUAL_PAYLOAD.pop(key, None)
    if not keys or not cleared_keys:
        _MANUAL_PAYLOAD = {}
        cleared_keys = ["*"]
    if not _MANUAL_PAYLOAD:
        _MAX_TORQUE = 0.0
    return {"cleared": cleared_keys}


@router.get("/cutting/test_payload", tags=["cutting"])
async def read_cutting_test_payload() -> Dict[str, Any]:
    """Expose current manual overrides for diagnostics."""
    return dict(_MANUAL_PAYLOAD)
