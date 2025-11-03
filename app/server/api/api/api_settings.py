from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.db.models.tool_record import ToolRecord
from app.server.api.services.settings_store import SettingsStore

from ..api_core import settings_router as router

_store = SettingsStore()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/parameters")
def get_all_parameters(session: Session = Depends(get_db_session)) -> dict:
    payload = _store.fetch_all(session)
    tools = session.query(ToolRecord).order_by(ToolRecord.id.asc()).all()
    return {"categories": payload, "tools": [record.to_dict() for record in tools]}


@router.get("/parameters/{category}")
def get_parameter_category(category: str, session: Session = Depends(get_db_session)) -> dict:
    _ensure_category(category)
    data = _store.fetch_category(session, category)
    return {"category": category, "payload": data}


@router.put("/parameters/{category}")
def update_parameter_category(
    category: str,
    payload: dict,
    session: Session = Depends(get_db_session),
) -> dict:
    _ensure_category(category)
    updated = _store.save_category(session, category, payload)
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
        raise HTTPException(status_code=400, detail="content 必须为字符串格式的 YAML")
    try:
        updated = _store.import_yaml(session, category, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"category": category, "payload": updated}


@router.get("/parameters/{category}/export")
def export_parameter_category(category: str, session: Session = Depends(get_db_session)) -> dict:
    _ensure_category(category)
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
        raise HTTPException(status_code=400, detail="tools 必须为数组")

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
    if category not in _store.list_categories():
        raise HTTPException(status_code=404, detail=f"未知参数类别: {category}")
