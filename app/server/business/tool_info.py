from __future__ import annotations

import threading
from typing import Any, Dict, Mapping, Optional, Sequence

from app.server.api.services.config_loader import ConfigSettingsLoader
from app.server.api.services.meta_loader import MetaDataLoader
from app.server.models import ToolInfoSnapshot


def _normalize(value: Any) -> Optional[str]:
    if value is None:
        return None
    try:
        text = str(value).strip()
    except Exception:
        return None
    return text or None


def _first_non_empty(values: Sequence[Any]) -> Optional[str]:
    for value in values:
        normalized = _normalize(value)
        if normalized:
            return normalized
    return None


class ToolInfoAssembler:
    """Aggregate tool information from status/configuration sources."""

    def __init__(
        self,
        *,
        config_loader: ConfigSettingsLoader | None = None,
        meta_loader: MetaDataLoader | None = None,
    ) -> None:
        self._config_loader = config_loader or ConfigSettingsLoader()
        self._meta_loader = meta_loader or MetaDataLoader()
        self._lock = threading.RLock()

    def build(self, status: Optional[Mapping[str, Any]] = None) -> ToolInfoSnapshot:
        with self._lock:
            status_payload = dict(status or {})

            # Tool usage comes directly from the live status snapshot.
            tool_usage = _first_non_empty(
                [
                    status_payload.get("tool_usage"),
                    status_payload.get("toolUsage"),
                    status_payload.get("tool_utilization"),
                ]
            )

            # Load meta/config data best effort.
            meta: Dict[str, Any] = {}
            try:
                meta = self._meta_loader.extract()
            except Exception:
                meta = {}

            tool_life = _first_non_empty(
                [
                    status_payload.get("tool_life"),
                    status_payload.get("toolLife"),
                    meta.get("tool_life"),
                ]
            )
            tool_diameter = _first_non_empty(
                [
                    status_payload.get("tool_diameter"),
                    status_payload.get("toolDiameter"),
                    status_payload.get("cutter_diameter"),
                    status_payload.get("cutterDiameter"),
                    meta.get("cutter_diameter"),
                ]
            )

            model = _first_non_empty(
                [
                    status_payload.get("tool_model"),
                    status_payload.get("toolModel"),
                    status_payload.get("tool_name"),
                    status_payload.get("toolName"),
                ]
            )

            try:
                settings = self._config_loader.get_settings_bundle()
            except Exception:
                settings = {}

            tool_table = settings.get("tool_table") or []
            if tool_table:
                first = tool_table[0]
                if isinstance(first, Mapping):
                    table_model = _first_non_empty(
                        [
                            first.get("name"),
                            first.get("code"),
                        ]
                    )
                    if not model and table_model:
                        model = table_model
                    table_diameter = _first_non_empty([first.get("diameter")])
                    if not tool_diameter and table_diameter:
                        tool_diameter = table_diameter

            payload: Dict[str, Any] = {}
            if model:
                payload["tool_model"] = model
            if tool_diameter:
                payload["tool_diameter"] = tool_diameter
            if tool_usage:
                payload["tool_usage"] = tool_usage
            if tool_life:
                payload["tool_life"] = tool_life

            return ToolInfoSnapshot.from_mapping(payload)


__all__ = ["ToolInfoAssembler"]
