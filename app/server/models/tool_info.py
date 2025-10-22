from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Sequence


def _first_value(data: Dict[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in data:
            return data.pop(key)
    return None


def _to_display(value: Any) -> str:
    if value is None:
        return "-"
    try:
        text = str(value).strip()
    except Exception:
        text = "-"
    return text or "-"


@dataclass
class ToolInfoSnapshot:
    """Canonical representation of tool information exposed via the API."""

    tool_model: str = "-"
    tool_diameter: str = "-"
    tool_usage: str = "-"
    tool_life: str = "-"
    extras: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "ToolInfoSnapshot":
        data = dict(payload or {})
        tool_model = _to_display(
            _first_value(data, ("tool_model", "toolModel", "tool_name", "toolName"))
        )
        tool_diameter = _to_display(
            _first_value(data, ("tool_diameter", "toolDiameter", "cutter_diameter", "cutterDiameter"))
        )
        tool_usage = _to_display(
            _first_value(data, ("tool_usage", "toolUsage", "usage", "utilization"))
        )
        tool_life = _to_display(
            _first_value(data, ("tool_life", "toolLife", "tool_lifetime", "toolLifetime"))
        )
        if not data:
            extras: Dict[str, Any] = {}
        else:
            extras = data
        return cls(
            tool_model=tool_model,
            tool_diameter=tool_diameter,
            tool_usage=tool_usage,
            tool_life=tool_life,
            extras=extras,
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self.extras)
        data.update(
            {
                "tool_model": self.tool_model,
                "tool_diameter": self.tool_diameter,
                "tool_usage": self.tool_usage,
                "tool_life": self.tool_life,
                # Provide camelCase aliases for UI compatibility.
                "toolModel": self.tool_model,
                "toolDiameter": self.tool_diameter,
                "toolUsage": self.tool_usage,
                "toolLifetime": self.tool_life,
            }
        )
        return data


__all__ = ["ToolInfoSnapshot"]
