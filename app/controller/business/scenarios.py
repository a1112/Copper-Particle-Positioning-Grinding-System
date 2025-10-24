from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


@dataclass
class Scenario:
    """Container describing one control snapshot to push to the server."""

    name: str
    status: Dict[str, Any]
    cutting: Optional[Dict[str, Any]] = None
    delay: float = 1.0
    logs: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "Scenario":
        name = str(payload.get("label") or payload.get("name") or "unnamed")
        status_payload = payload.get("status") or {}
        cutting_payload = payload.get("cutting")
        logs_payload = payload.get("logs")
        delay_value = payload.get("delay", 1.0)
        try:
            delay = float(delay_value)
        except Exception:
            delay = 1.0
        if delay < 0:
            delay = 0.0

        logs: Optional[List[Dict[str, Any]]] = None
        if isinstance(logs_payload, Iterable):
            parsed: List[Dict[str, Any]] = []
            for entry in logs_payload:
                if isinstance(entry, Mapping):
                    parsed.append(dict(entry))
            if parsed:
                logs = parsed

        return cls(
            name=name,
            status=dict(status_payload),
            cutting=dict(cutting_payload) if isinstance(cutting_payload, Mapping) else None,
            delay=delay,
            logs=logs,
        )


def load_scenarios(paths: Iterable[Path]) -> List[Scenario]:
    scenarios: List[Scenario] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            items = payload
        else:
            items = payload.get("scenarios") if isinstance(payload, dict) else None
            if not isinstance(items, list):
                raise ValueError(f"Unsupported scenario file format: {path}")
        for item in items:
            if isinstance(item, dict):
                scenarios.append(Scenario.from_mapping(item))
    if not scenarios:
        raise ValueError("No scenarios were loaded")
    return scenarios
