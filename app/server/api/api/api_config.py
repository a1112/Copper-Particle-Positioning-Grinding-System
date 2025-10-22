from __future__ import annotations

from starlette.responses import JSONResponse

from app.server.api.services.config_loader import ConfigSettingsLoader
from app.server.api.services.meta_loader import MetaDataLoader

from ..api_core import config_router as router

_SETTINGS_LOADER = ConfigSettingsLoader()
_META_LOADER = MetaDataLoader()


@router.get('/config/meta')
async def config_meta():
    try:
        return _META_LOADER.extract()
    except Exception as e:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(e)})


@router.get('/config/settings')
async def config_settings():
    try:
        return _SETTINGS_LOADER.get_settings_bundle()
    except Exception as exc:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(exc)})
