from __future__ import annotations

from datetime import datetime

import yaml

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.tasks import TaskStatus
from app.common.task_actions import PARAM_UPDATE_ACTION, friendly_action_name, friendly_action_type, normalise_action
from app.db import SessionLocal
from app.db.models.hardware_task_queue import HardwareTaskQueue
from app.db.models.tool_record import ToolRecord
from app.server.api.services.auto_config_loader import AutoConfigLoader
from app.server.api.services.settings_store import SettingsStore

from ..api_core import settings_router as router

_store = SettingsStore()
_auto_loader = AutoConfigLoader()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/parameters")
def get_all_parameters(session: Session = Depends(get_db_session)) -> dict:
    payload = _store.fetch_all(session)
    payload["by_auto"] = _auto_loader.build_all(session)
    tools = session.query(ToolRecord).order_by(ToolRecord.id.asc()).all()
    return {"categories": payload, "tools": [record.to_dict() for record in tools]}


@router.get("/parameters/{category}")
def get_parameter_category(category: str, session: Session = Depends(get_db_session)) -> dict:
    _ensure_category(category)
    if _is_auto_category(category):
        data = _auto_loader.build_category(session, category) or {}
    else:
        data = _store.fetch_category(session, category)
    return {"category": category, "payload": data}


@router.put("/parameters/{category}")
def update_parameter_category(
    category: str,
    payload: dict,
    session: Session = Depends(get_db_session),
) -> dict:
    _ensure_category(category)
    _store.save_category(session, category, payload)
    _enqueue_param_update_task(session, category)
    if _is_auto_category(category):
        updated = _auto_loader.build_category(session, category) or {}
    else:
        updated = _store.fetch_category(session, category)
    return {"category": category, "payload": updated}


@router.post("/parameters/{category}/import")
def import_parameter_category(
    category: str,
    body: dict,
    session: Session = Depends(get_db_session),
) -> dict:
    _ensure_category(category)
    content = body.get("content")
    if not isinstance(content, str):
        raise HTTPException(status_code=400, detail="content \u5fc5\u987b\u4e3a\u5b57\u7b26\u4e32\u683c\u5f0f (YAML)")
    try:
        if _is_auto_category(category):
            data = yaml.safe_load(content) or {}
            if not isinstance(data, dict):
                raise ValueError("导入的配置必须是字典结构")
            _store.save_category(session, category, data)
        else:
            _store.import_yaml(session, category, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _enqueue_param_update_task(session, category)
    payload = _auto_loader.build_category(session, category) if _is_auto_category(category) else _store.fetch_category(session, category)
    return {"category": category, "payload": payload or {}}


@router.get("/parameters/{category}/export")
def export_parameter_category(category: str, session: Session = Depends(get_db_session)) -> dict:
    _ensure_category(category)
    if _is_auto_category(category):
        yaml_text = _auto_loader.export_yaml(session, category)
    else:
        yaml_text = _store.export_yaml(session, category)
    return {"category": category, "content": yaml_text}


@router.get("/tools")
def get_tool_parameters(session: Session = Depends(get_db_session)) -> dict:
    records = session.query(ToolRecord).order_by(ToolRecord.id.asc()).all()
    return {"tools": [record.to_dict() for record in records]}


@router.put("/tools")
def update_tool_parameters(payload: dict, session: Session = Depends(get_db_session)) -> dict:
    items = payload.get("tools")
    if not isinstance(items, list):
        raise HTTPException(status_code=400, detail="tools \u5fc5\u987b\u4e3a\u6570\u7ec4")

    existing = {row.id: row for row in session.query(ToolRecord).all()}
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        tool_id = item.get("id")
        if tool_id and tool_id in existing:
            row = existing[tool_id]
        else:
            row = ToolRecord()
            session.add(row)
        if "model" in item:
            row.model = str(item["model"] or "")
        if "diameter_mm" in item:
            row.diameter_mm = float(item["diameter_mm"] or 0)
        if "length_mm" in item:
            row.length_mm = float(item["length_mm"] or 0)
        if "usage_minutes" in item:
            row.usage_minutes = int(item["usage_minutes"] or 0)
        if "service_life_minutes" in item:
            row.service_life_minutes = int(item["service_life_minutes"] or 0)
        if "status" in item:
            row.status = int(item["status"] or 0)
        result.append(row)

    session.commit()
    return {"tools": [row.to_dict() for row in result]}


def _ensure_category(category: str) -> None:
    if category not in _store.list_categories() and not _is_auto_category(category):
        raise HTTPException(status_code=404, detail=f"\u672a\u77e5\u53c2\u6570\u7c7b\u522b: {category}")


def _enqueue_param_update_task(session: Session, category: str) -> HardwareTaskQueue:
    """Record a parameter update so downstream hardware can pick up changes."""
    action_key = PARAM_UPDATE_ACTION
    task = HardwareTaskQueue(
        task_name=friendly_action_name(action_key),
        task_type=friendly_action_type(action_key),
        device_id=1,
        task_params={
            "action": action_key,
            "action_key": normalise_action(action_key),
            "action_name": friendly_action_name(action_key),
            "params": {"category": category},
            "category": category,
            "queued_at": datetime.utcnow().timestamp(),
        },
        status=int(TaskStatus.PENDING),
        status_params={"phase": "queued"},
        created_by="api.settings",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def _is_auto_category(category: str) -> bool:
    return category in _auto_loader.list_categories()
