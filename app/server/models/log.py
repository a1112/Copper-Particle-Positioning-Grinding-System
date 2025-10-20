from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping


@dataclass
class LogEntry:
    """Log line captured from the runtime buffer."""

    ts: float
    time_text: str
    level: str
    name: str
    message: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "LogEntry":
        return cls(
            ts=float(payload.get("ts", 0.0) or 0.0),
            time_text=str(payload.get("time", "")),
            level=str(payload.get("level", "")).upper(),
            name=str(payload.get("name", "")),
            message=str(payload.get("msg", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts,
            "time": self.time_text,
            "level": self.level,
            "name": self.name,
            "msg": self.message,
        }
