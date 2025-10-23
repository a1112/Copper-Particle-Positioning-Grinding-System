from __future__ import annotations

import asyncio
import math
import time
from typing import Any, Dict, List, Optional

from app.domain.status import get_status_service
from app.server.models import (
    ControlCommand,
    ControlResult,
    CuttingSnapshot,
    StatusModel,
)
from app.server.utils import logs

from .base import BusinessService


class SimBusinessService(BusinessService):
    """Business layer backed by simulator data sources."""

    def __init__(self) -> None:
        self._status_service = get_status_service()
        self._cutting_start = time.monotonic()
        self._cutting_max_torque = 0.0
        self._cutting_override: Dict[str, Any] = {}

    async def fetch_status(self) -> StatusModel:
        payload = await asyncio.to_thread(self._status_service.fetch_status)
        return StatusModel.from_mapping(payload)

    async def execute_control(self, command: ControlCommand) -> ControlResult:
        logs.push("INFO", "control", f"[sim] command={command.action}")
        return ControlResult.success(message="Simulated control executed", details={"action": command.action})

    async def fetch_cutting(self) -> CuttingSnapshot:
        payload = self._build_cutting_payload()
        return CuttingSnapshot.from_mapping(payload)

    async def apply_cutting_override(self, payload: Dict[str, Any], *, merge: bool = False) -> Dict[str, Any]:
        if not merge:
            self._cutting_override.clear()
        if payload:
            self._cutting_override.update(payload)
        return dict(self._cutting_override)

    async def get_cutting_override(self) -> Dict[str, Any]:
        return dict(self._cutting_override)

    async def clear_cutting_override(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        if keys:
            for key in keys:
                self._cutting_override.pop(key, None)
        else:
            self._cutting_override.clear()
        return dict(self._cutting_override)

    def add_log(self, entry: Dict[str, Any]) -> None:
        level = str(entry.get("level", "INFO"))
        name = str(entry.get("name", "sim"))
        msg = str(entry.get("msg", entry.get("message", "")))
        ts = entry.get("ts")
        logs.push(level, name, msg, ts=ts if isinstance(ts, (int, float)) else None)

    def _build_cutting_payload(self) -> Dict[str, Any]:
        elapsed = time.monotonic() - self._cutting_start
        feed_rate = 20.0 + 5.0 * math.sin(elapsed * 0.5)
        downfeed_target = 0.8
        downfeed_current = min(downfeed_target, max(0.0, downfeed_target * (elapsed / 10.0)))
        removal_expected = 120.0
        removal_current = min(removal_expected, max(0.0, removal_expected * (elapsed / 20.0)))
        torque = 0.3 + 0.2 * abs(math.sin(elapsed * 0.8)) + 0.05 * abs(math.sin(elapsed * 1.7))

        self._cutting_max_torque = max(self._cutting_max_torque, torque)

        payload: Dict[str, Any] = {
            "ts": time.time(),
            "feed_rate": round(feed_rate, 3),
            "downfeed_target": round(downfeed_target, 3),
            "downfeed_current": round(downfeed_current, 3),
            "removal_current": round(removal_current, 3),
            "removal_expected": round(removal_expected, 3),
            "torque_max": round(self._cutting_max_torque, 3),
            "torque": round(torque, 3),
            "elapsed_sec": round(elapsed, 2),
        }

        payload = self._merge_cutting_override(payload)
        payload["torque_max"] = self._normalize_torque_max(payload)
        return payload

    def _merge_cutting_override(self, base: Dict[str, Any]) -> Dict[str, Any]:
        if not self._cutting_override:
            return base
        merged = dict(base)
        merged.update(self._cutting_override)
        return merged

    @staticmethod
    def _normalize_torque_max(payload: Dict[str, Any]) -> float:
        def _to_float(value: Any) -> float:
            try:
                return float(value)
            except Exception:
                return 0.0

        torque_value = _to_float(payload.get("torque", 0.0))
        torque_max_value = _to_float(payload.get("torque_max", 0.0))
        return round(max(torque_max_value, torque_value), 3)
