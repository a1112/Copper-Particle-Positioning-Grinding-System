from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from ..api_core import tool_router as router
from app.db import SessionLocal
from app.db.models.tool_record import ToolRecord


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/toolList")
def tool_list(session: Session = Depends(get_db_session)) -> list[dict]:
    records = session.query(ToolRecord).order_by(ToolRecord.id.asc()).all()
    return [record.to_dict() for record in records]
