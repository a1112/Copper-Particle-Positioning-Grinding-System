from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import json
from starlette.responses import JSONResponse

from app.server.api.services.config_loader import ConfigSettingsLoader

from ..api_core import config_router as router

_BASE = Path(__file__).resolve().parents[4]
_FILE = _BASE / 'docs' / 'MzPoliShine.km'
_SETTINGS_LOADER = ConfigSettingsLoader()


def _load_texts() -> list[str]:
    if not _FILE.exists():
        return []
    data: Dict[str, Any]
    try:
        raw = _FILE.read_bytes()
        # Try utf-8 first
        try:
            data = json.loads(raw.decode('utf-8'))
        except Exception:
            # Fallback to GBK/CP936
            data = json.loads(raw.decode('gbk', errors='ignore'))
    except Exception:
        return []

    texts: list[str] = []
    def walk(node: Dict[str, Any]):
        d = node.get('data') or {}
        t = d.get('text')
        if isinstance(t, str):
            texts.append(t)
        for ch in node.get('children') or []:
            walk(ch)
    root = data.get('root') or {}
    walk(root)
    return texts


@router.get('/config/meta')
async def config_meta():
    try:
        texts = _load_texts()
        # Heuristic extraction
        def find_first(keys: list[str]) -> str | None:
            for t in texts:
                for k in keys:
                    if k in t:
                        return t
            return None
        # Basic fields (best-effort)
        cutter_diameter = find_first(['??', '????']) or ''
        tool_life = find_first(['??', '????']) or ''
        control_mode = find_first(['????']) or ''
        stage_mode = find_first(['???', '????']) or ''
        plane_height = find_first(['????', '????']) or ''
        board_serial = find_first(['???', '??']) or ''
        particle_count = find_first(['????', '????']) or ''
        # Stats
        meta = {
            'nodes': len(texts),
            'cutter_diameter': cutter_diameter,
            'tool_life': tool_life,
            'control_mode': control_mode,
            'stage_mode': stage_mode,
            'plane_height': plane_height,
            'board_serial': board_serial,
            'particle_count': particle_count,
        }
        return meta
    except Exception as e:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(e)})


@router.get('/config/settings')
async def config_settings():
    try:
        return _SETTINGS_LOADER.get_settings_bundle()
    except Exception as exc:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(exc)})
