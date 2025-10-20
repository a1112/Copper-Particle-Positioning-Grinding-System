from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class StatusModel:
    """Canonical representation of machine status exchanged with the API layer."""

    state: str = "-"
    position: Dict[str, Any] = field(default_factory=dict)
    spindle_rpm: float = 0.0
    spindle_torque: float = 0.0
    extras: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "StatusModel":
        data = dict(payload or {})
        state = str(data.pop("state", "-") or "-")
        position = data.pop("position", {}) or {}
        spindle_rpm = cls._to_float(data.pop("spindle_rpm", 0.0))
        spindle_torque = cls._to_float(data.pop("spindle_torque", 0.0))
        return cls(
            state=state,
            position=position,
            spindle_rpm=spindle_rpm,
            spindle_torque=spindle_torque,
            extras=data,
        )

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self.extras)
        data["state"] = self.state
        data["position"] = self.position
        data["spindle_rpm"] = self.spindle_rpm
        data["spindle_torque"] = self.spindle_torque
        return data
