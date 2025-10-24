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
    program: Optional[List[str]] = None
    program_state: Optional[Dict[str, Any]] = None

    @staticmethod
    def _normalize_program(source: Any) -> List[str]:
        if source is None:
            return []
        if isinstance(source, (bytes, bytearray)):
            source = source.decode("utf-8", errors="ignore")
        if isinstance(source, str):
            raw = source.splitlines()
        else:
            try:
                raw = list(source)
            except TypeError as exc:
                raise ValueError("Program must be a string or a sequence of strings") from exc
        lines: List[str] = []
        for item in raw:
            if item is None:
                continue
            text = str(item)
            if text.endswith("\r"):
                text = text[:-1]
            lines.append(text)
        return lines

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

        program: Optional[List[str]] = None
        if "program" in payload or "gcode" in payload or "code" in payload:
            source = payload.get("program", payload.get("gcode", payload.get("code")))
            program = cls._normalize_program(source)

        program_state_payload = payload.get("program_state") or payload.get("code_state")
        program_state: Optional[Dict[str, Any]] = None
        if isinstance(program_state_payload, Mapping):
            program_state = dict(program_state_payload)

        return cls(
            name=name,
            status=dict(status_payload),
            cutting=dict(cutting_payload) if isinstance(cutting_payload, Mapping) else None,
            delay=delay,
            logs=logs,
            program=program,
            program_state=program_state,
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
