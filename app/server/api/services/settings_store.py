from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.param_settings import ParamSettings


class SettingsStore:
    """Persist parameter categories in the database with YAML fallbacks."""

    DEFAULT_CATEGORIES: Dict[str, str] = {
        "general": "general.yaml",
        "process": "process.yaml",
        "algorithm": "algorithm.yaml",
    }

    def __init__(self, config_dir: str | Path | None = None) -> None:
        base = Path(__file__).resolve().parents[4] / "configs"
        self._directory = Path(config_dir) if config_dir else base / "parameters"
        self._directory.mkdir(parents=True, exist_ok=True)

    # Public API -------------------------------------------------------------

    def list_categories(self) -> Iterable[str]:
        return self.DEFAULT_CATEGORIES.keys()

    def fetch_all(self, session: Session) -> Dict[str, dict]:
        payload: Dict[str, dict] = {}
        for category in self.list_categories():
            payload[category] = self.fetch_category(session, category)
        return payload

    def fetch_category(self, session: Session, category: str) -> dict:
        row = session.execute(
            select(ParamSettings).where(ParamSettings.category == category)
        ).scalar_one_or_none()
        if row:
            return row.payload or {}
        default_data = self._load_default(category)
        if default_data is not None:
            row = ParamSettings(category=category, payload=default_data)
            session.add(row)
            session.commit()
            session.refresh(row)
            return default_data
        return {}

    def save_category(self, session: Session, category: str, payload: dict, updated_by: str | None = None) -> dict:
        row = session.execute(
            select(ParamSettings).where(ParamSettings.category == category)
        ).scalar_one_or_none()
        if row is None:
            row = ParamSettings(category=category, payload=payload, updated_by=updated_by)
            session.add(row)
        else:
            row.payload = payload
            row.updated_by = updated_by
        session.commit()
        session.refresh(row)
        return row.payload or {}

    def export_yaml(self, session: Session, category: str) -> str:
        payload = self.fetch_category(session, category)
        return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)

    def import_yaml(self, session: Session, category: str, yaml_text: str, updated_by: str | None = None) -> dict:
        data = yaml.safe_load(yaml_text) or {}
        if not isinstance(data, dict):
            raise ValueError("Imported YAML必须是字典结构")
        return self.save_category(session, category, data, updated_by=updated_by)

    # Internal helpers ------------------------------------------------------

    def _load_default(self, category: str) -> dict | None:
        filename = self.DEFAULT_CATEGORIES.get(category)
        if not filename:
            return {}
        path = self._directory / filename
        if not path.exists():
            return {}
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ValueError(f"配置文件 {path} 必须是字典")
        return data


__all__ = ["SettingsStore"]
