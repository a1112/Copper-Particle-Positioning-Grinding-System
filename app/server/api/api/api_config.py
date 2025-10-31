from __future__ import annotations

from starlette.responses import JSONResponse

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.db.models.tool_record import ToolRecord
from app.server.api.services.settings_store import SettingsStore
from app.server.api.services.meta_loader import MetaDataLoader

from ..api_core import config_router as router

_SETTINGS_STORE = SettingsStore()
_META_LOADER = MetaDataLoader()


@router.get('/config/meta')
async def config_meta():
    try:
        return _META_LOADER.extract()
    except Exception as e:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(e)})


@router.get('/config/settings')
async def config_settings():
    session: Session = SessionLocal()
    try:
        categories = _SETTINGS_STORE.fetch_all(session)
        tools = session.query(ToolRecord).order_by(ToolRecord.id.asc()).all()
        return {"categories": categories, "tools": [record.to_dict() for record in tools]}
    except Exception as exc:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(exc)})
    finally:
        session.close()
