from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class CuttingSnapshot:
    """Canonical representation of cutting telemetry exchanged with the API."""

    ts: float = 0.0
    feed_rate: float = 0.0
    downfeed_target: float = 0.0
    downfeed_current: float = 0.0
    removal_current: float = 0.0
    removal_expected: float = 0.0
    torque_max: float = 0.0
    torque: float = 0.0
    elapsed_sec: float = 0.0
    extras: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "CuttingSnapshot":
        data = dict(payload or {})
        ts = cls._to_float(data.pop("ts", 0.0))
        feed_rate = cls._to_float(data.pop("feed_rate", 0.0))
        downfeed_target = cls._to_float(data.pop("downfeed_target", 0.0))
        downfeed_current = cls._to_float(data.pop("downfeed_current", 0.0))
        removal_current = cls._to_float(data.pop("removal_current", 0.0))
        removal_expected = cls._to_float(data.pop("removal_expected", 0.0))
        torque_max = cls._to_float(data.pop("torque_max", 0.0))
        torque = cls._to_float(data.pop("torque", 0.0))
        elapsed_sec = cls._to_float(data.pop("elapsed_sec", 0.0))
        extras = data
        return cls(
            ts=ts,
            feed_rate=feed_rate,
            downfeed_target=downfeed_target,
            downfeed_current=downfeed_current,
            removal_current=removal_current,
            removal_expected=removal_expected,
            torque_max=torque_max,
            torque=torque,
            elapsed_sec=elapsed_sec,
            extras=extras,
        )

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self.extras)
        data["ts"] = self.ts
        data["feed_rate"] = self.feed_rate
        data["downfeed_target"] = self.downfeed_target
        data["downfeed_current"] = self.downfeed_current
        data["removal_current"] = self.removal_current
        data["removal_expected"] = self.removal_expected
        data["torque_max"] = max(self.torque_max, self.torque)
        data["torque"] = self.torque
        data["elapsed_sec"] = self.elapsed_sec
        return data
