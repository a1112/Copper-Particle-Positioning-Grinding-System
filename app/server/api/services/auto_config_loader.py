from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.param_settings import ParamSettings


class AutoConfigLoader:
    """Load dynamic configuration definitions from template YAML files."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        root = Path(__file__).resolve().parents[4]
        self._base_dir = Path(base_dir) if base_dir else root / "configs" / "template" / "configs"
        self._templates = self._load_templates()

    # ------------------------------------------------------------------ public

    def list_categories(self) -> List[str]:
        return list(self._templates.keys())

    def build_all(self, session: Session) -> Dict[str, dict]:
        payload: Dict[str, dict] = {}
        for category in self.list_categories():
            built = self.build_category(session, category)
            if built:
                payload[category] = built
        return payload

    def build_category(self, session: Session, category: str) -> Optional[dict]:
        template = self._templates.get(category)
        if not template:
            return None
        values = self._resolve_values(session, category, template["defaults"])
        groups = []
        for group in template["groups"]:
            group_copy = {"id": group["id"], "label": group["label"], "fields": []}
            group_values = values.get(group["id"], {})
            for field in group["fields"]:
                resolved = dict(field)
                resolved["value"] = group_values.get(field["id"], field["default"])
                group_copy["fields"].append(resolved)
            groups.append(group_copy)
        flattened = self._flatten_values(groups)
        return {
            "id": template["id"],
            "label": template["label"],
            "groups": groups,
            "values": flattened,
        }

    def export_yaml(self, session: Session, category: str) -> str:
        built = self.build_category(session, category)
        values = built.get("values", {}) if built else {}
        return yaml.safe_dump(values, allow_unicode=True, sort_keys=False)

    # ---------------------------------------------------------------- internal

    def _load_templates(self) -> Dict[str, dict]:
        templates: Dict[str, dict] = {}
        if not self._base_dir.exists():
            return templates
        for path in sorted(self._base_dir.glob("*.yaml")):
            parsed = self._parse_template(path)
            if parsed:
                templates[parsed["id"]] = parsed
        return templates

    def _parse_template(self, path: Path) -> Optional[dict]:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            return None
        if not isinstance(data, dict):
            return None
        category_id = str(data.get("id") or path.stem)
        label = str(data.get("label") or category_id)
        groups = []
        defaults: Dict[str, Dict[str, object]] = {}
        for group_name, raw_group in data.items():
            if group_name in {"id", "label"}:
                continue
            if not isinstance(raw_group, dict):
                continue
            group_label = raw_group.get("label", group_name) if isinstance(raw_group.get("label"), str) else group_name
            fields = []
            for field_id, raw_field in raw_group.items():
                if field_id == "label":
                    continue
                field_label = field_id
                field_type = "TextField"
                default_value: object = 0
                if isinstance(raw_field, dict):
                    field_label = raw_field.get("label", field_label) or field_id
                    field_type = raw_field.get("type", field_type) or "TextField"
                    default_value = raw_field.get("default", raw_field.get("value", 0))
                else:
                    default_value = raw_field
                fields.append(
                    {
                        "id": field_id,
                        "label": field_label,
                        "type": field_type,
                        "default": default_value if default_value is not None else 0,
                    }
                )
                defaults.setdefault(group_name, {})[field_id] = default_value if default_value is not None else 0
            if fields:
                groups.append(
                    {
                        "id": group_name,
                        "label": group_label,
                        "fields": fields,
                    }
                )
        return {"id": category_id, "label": label, "groups": groups, "defaults": defaults}

    def _resolve_values(self, session: Session, category: str, defaults: dict) -> dict:
        stored = session.execute(
            select(ParamSettings).where(ParamSettings.category == category)
        ).scalar_one_or_none()
        if stored and isinstance(stored.payload, dict):
            return self._merge_defaults(deepcopy(defaults), stored.payload)
        return deepcopy(defaults)

    @staticmethod
    def _merge_defaults(defaults: dict, override: dict) -> dict:
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(defaults.get(key), dict):
                defaults[key] = AutoConfigLoader._merge_defaults(defaults[key], value)
            else:
                defaults[key] = value
        return defaults

    @staticmethod
    def _flatten_values(groups: List[dict]) -> dict:
        flattened: Dict[str, dict] = {}
        for group in groups:
            group_id = group["id"]
            for field in group.get("fields", []):
                flattened.setdefault(group_id, {})[field["id"]] = field.get("value", field.get("default"))
        return flattened


__all__ = ["AutoConfigLoader"]
