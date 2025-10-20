from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


@dataclass
class ControlCommand:
    """Generic control command dispatched from the API."""

    action: str
    params: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, action: str, params: Optional[Mapping[str, Any]] = None) -> "ControlCommand":
        return cls(action=action, params=dict(params or {}))


@dataclass
class ControlResult:
    """Outcome of a control command execution."""

    ok: bool
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"ok": self.ok}
        if self.message:
            payload["message"] = self.message
        if self.details:
            payload["details"] = self.details
        return payload

    @classmethod
    def success(cls, message: str = "", details: Optional[Mapping[str, Any]] = None) -> "ControlResult":
        return cls(ok=True, message=message, details=dict(details or {}))

    @classmethod
    def failure(cls, message: str, details: Optional[Mapping[str, Any]] = None) -> "ControlResult":
        return cls(ok=False, message=message, details=dict(details or {}))
