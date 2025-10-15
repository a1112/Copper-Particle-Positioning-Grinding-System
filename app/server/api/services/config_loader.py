"""Helpers for exposing structured configuration data via the API."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml


class ConfigSettingsLoader:
    """Load and normalize job/machine configuration for API consumption."""

    def __init__(self, configs_root: str | Path | None = None) -> None:
        base = Path(__file__).resolve().parents[4]
        default_dir = base / "configs"
        self._configs_dir = Path(configs_root) if configs_root else default_dir
        self._job_path = self._configs_dir / "job_default.yaml"
        self._machine_path = self._configs_dir / "machine.yaml"
        self._desc_path = self._configs_dir / "settings_descriptions.yaml"

    # Public -----------------------------------------------------------------

    def get_settings_bundle(self) -> Dict[str, Any]:
        """Return a structured view that the UI can render directly."""
        job_data = self._load_job_config()
        machine_data = self._load_machine_config()
        descriptions = self._load_descriptions()

        tool_table = self._format_tool_table(machine_data.get("tool", {}))
        calibration_sections = (
            self._format_sections(machine_data.get("calib", {}), descriptions=descriptions, root_prefix="calib")
            + self._format_sections(
                machine_data.get("workoffset", {}),
                prefix="workoffset",
                descriptions=descriptions,
                root_prefix="workoffset",
            )
        )
        machine_sections = self._format_sections(
            machine_data.get("machine", {}),
            descriptions=descriptions,
            root_prefix="machine",
        )
        safety_sections = self._format_sections(
            machine_data.get("safety", {}),
            descriptions=descriptions,
            root_prefix="safety",
        )
        monitor_items = self._format_items(
            machine_data.get("monitor_defaults", {}),
            section="monitor_defaults",
            descriptions=descriptions,
        )

        bundle: Dict[str, Any] = {
            "sources": {
                "job": str(self._job_path),
                "machine": str(self._machine_path),
            },
            "job_sections": self._format_sections(job_data, descriptions=descriptions),
            "calibration_sections": calibration_sections,
            "machine_sections": machine_sections,
            "safety_sections": safety_sections,
            "monitor_defaults": monitor_items,
            "tool_table": tool_table,
        }
        return bundle

    # Internal helpers -------------------------------------------------------

    def _load_job_config(self) -> Dict[str, Any]:
        if not self._job_path.exists():
            return {}
        text = self._read_text_with_fallback(self._job_path)
        try:
            data = yaml.safe_load(text) or {}
            if not isinstance(data, dict):
                return {}
            return data
        except Exception:
            return {}

    def _load_descriptions(self) -> Dict[str, str]:
        if not self._desc_path.exists():
            return {}
        try:
            text = self._read_text_with_fallback(self._desc_path)
            data = yaml.safe_load(text) or {}
            if not isinstance(data, dict):
                return {}
            return {str(k): str(v) for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}
        except Exception:
            return {}

    def _load_machine_config(self) -> Dict[str, Any]:
        if not self._machine_path.exists():
            return {}
        raw = self._read_text_with_fallback(self._machine_path)
        normalized = self._normalize_machine_yaml(raw)
        try:
            data = yaml.safe_load(normalized) or {}
            if not isinstance(data, dict):
                return {}
            return data
        except Exception:
            return {}

    def _read_text_with_fallback(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # GBK fallback for legacy exports
            return path.read_text(encoding="gbk", errors="ignore")

    def _normalize_machine_yaml(self, text: str) -> str:
        """The machine template uses a quasi-YAML style; fix it to real YAML."""
        processed: List[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                processed.append(line)
                continue

            comment = ""
            body = line
            if "#" in line:
                idx = line.index("#")
                body = line[:idx]
                comment = line[idx:]

            body = body.rstrip()
            if ":" not in body:
                indent_len = len(body) - len(body.lstrip(" "))
                indent = body[:indent_len]
                rest = body[indent_len:]
                if rest and not rest.lstrip().startswith("-"):
                    parts = rest.strip().split(None, 1)
                    key = parts[0]
                    value = parts[1] if len(parts) > 1 else ""
                    body = f"{indent}{key}"
                    if value:
                        body += f": {value}"
                    else:
                        body += ":"

            # Ensure comments remain readable
            spacer = ""
            if comment:
                spacer = " " if not body.endswith(" ") else ""
            processed.append(body + spacer + comment)

        normalized = "\n".join(processed)

        # Inline maps use "{ key value, ... }" format; convert to YAML "{ key: value, ... }"
        brace_pattern = re.compile(r"\{([^{}]+)\}")

        def repl(match: re.Match[str]) -> str:
            inner = match.group(1)
            parts: List[str] = []
            for chunk in inner.split(","):
                chunk = chunk.strip()
                if not chunk:
                    continue
                tokens = chunk.split(None, 1)
                if len(tokens) == 2:
                    parts.append(f"{tokens[0]}: {tokens[1]}")
                else:
                    parts.append(f"{tokens[0]}:")
            return "{ " + ", ".join(parts) + " }"

        return brace_pattern.sub(repl, normalized)

    # Formatting helpers -----------------------------------------------------

    def _format_sections(
        self,
        data: Any,
        *,
        prefix: str | None = None,
        descriptions: Dict[str, str],
        root_prefix: str | None = None,
    ) -> List[Dict[str, Any]]:
        if not isinstance(data, dict):
            return []
        sections: List[Dict[str, Any]] = []
        for key, value in data.items():
            section_name = f"{prefix}.{key}" if prefix else str(key)
            full_section = section_name
            if root_prefix and not full_section.startswith(root_prefix):
                full_section = f"{root_prefix}.{full_section}"

            if isinstance(value, dict):
                entries = self._flatten_dict(value, prefix=full_section)
                items = self._build_items(entries, full_section, descriptions)
            else:
                display_key = section_name.split(".")[-1]
                items = [
                    self._build_item(display_key, full_section, value, descriptions),
                ]
            sections.append({"name": section_name, "items": items})
        return sections

    def _format_items(
        self,
        data: Any,
        *,
        section: str,
        descriptions: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        if not isinstance(data, dict):
            return []
        entries = self._flatten_dict(data, prefix=section)
        return self._build_items(entries, section, descriptions)

    def _flatten_dict(self, data: Dict[str, Any], *, prefix: str | None = None) -> List[Tuple[str, Any]]:
        items: List[Tuple[str, Any]] = []
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, prefix=path))
            else:
                items.append((path, value))
        return items

    def _build_items(
        self,
        entries: Iterable[Tuple[str, Any]],
        section_path: str,
        descriptions: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        formatted: List[Dict[str, Any]] = []
        prefix = f"{section_path}."
        for full_key, value in entries:
            display_key = full_key[len(prefix):] if full_key.startswith(prefix) else full_key
            formatted.append(self._build_item(display_key, full_key, value, descriptions))
        return formatted

    def _build_item(
        self,
        display_key: str,
        full_key: str,
        value: Any,
        descriptions: Dict[str, str],
    ) -> Dict[str, Any]:
        return {
            "key": display_key,
            "value": self._format_value(value),
            "description": descriptions.get(full_key, ""),
        }

    def _format_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            text = f"{value:.6f}".rstrip("0").rstrip(".")
            return text if text else "0"
        if isinstance(value, (int,)):
            return str(value)
        if isinstance(value, list):
            try:
                return json.dumps(value, ensure_ascii=False)
            except Exception:
                return str(value)
        if isinstance(value, dict):
            try:
                return json.dumps(value, ensure_ascii=False)
            except Exception:
                return str(value)
        if value is None:
            return "-"
        return str(value)

    def _format_tool_table(self, section: Any) -> List[Dict[str, Any]]:
        if not isinstance(section, dict):
            return []
        table = section.get("table")
        if not isinstance(table, dict):
            return []
        rows: List[Dict[str, Any]] = []
        for code, payload in table.items():
            if not isinstance(payload, dict):
                continue
            rows.append(
                {
                    "code": str(code),
                    "name": str(payload.get("name", "")),
                    "diameter": self._format_value(payload.get("diameter")),
                    "length": self._format_value(payload.get("length")),
                }
            )
        rows.sort(key=lambda row: row["code"])
        return rows


__all__ = ["ConfigSettingsLoader"]
