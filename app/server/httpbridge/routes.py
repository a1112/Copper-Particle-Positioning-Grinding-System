from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body

from .store import HttpDataStore
from app.server.data import get_backend
from app.server.utils import logs

log = logging.getLogger("app.httpbridge.routes")

bridge_router = APIRouter(prefix="/bridge", tags=["bridge"])

_STORE: Optional[HttpDataStore] = None


def set_store(store: HttpDataStore) -> None:
    """Register the shared store used by bridge endpoints."""
    global _STORE
    _STORE = store


def _require_store() -> HttpDataStore:
    if _STORE is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="HTTP bridge is not configured")
    return _STORE


@bridge_router.get("/ping")
async def ping() -> Dict[str, Any]:
    return {"ok": True}


@bridge_router.post("/status")
async def push_status(payload: Any = Body(...), store: HttpDataStore = Depends(_require_store)) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        try:
            payload = dict(payload or {})
        except Exception:
            payload = {"value": payload}
    store.update_status(payload or {})
    try:
        log.debug("Bridge status updated (keys=%s)", list(payload or {}).keys())
    except Exception:
        log.debug("Bridge status updated (type=%s)", type(payload).__name__)
    return {"ok": True}


@bridge_router.post("/cutting")
async def push_cutting(payload: Dict[str, Any] = Body(...), store: HttpDataStore = Depends(_require_store)) -> Dict[str, Any]:
    store.update_cutting(payload or {})
    return {"ok": True}


def _mirror_entry(entry: Dict[str, Any]) -> None:
    backend = None
    try:
        backend = get_backend()
    except Exception:
        backend = None
    if backend is not None:
        try:
            backend.add_log(entry)
            return
        except Exception:
            pass
    level = str(entry.get("level", "INFO"))
    name = str(entry.get("name", "http"))
    msg = str(entry.get("msg", entry.get("message", "")))
    ts = entry.get("ts")
    logs.push(level, name, msg, ts=ts if isinstance(ts, (int, float)) else None)


@bridge_router.post("/logs")
async def push_logs(entries: Any = Body(...), store: HttpDataStore = Depends(_require_store)) -> Dict[str, Any]:
    if isinstance(entries, dict):
        mapped = dict(entries)
        store.append_log(mapped)
        _mirror_entry(mapped)
        return {"ok": True}

    iterable: Iterable[Any]
    if isinstance(entries, list):
        iterable = entries
    else:
        iterable = list(entries)
        entry = {"message": str(entries)}
        store.append_log(entry)
        _mirror_entry(entry)
        return {"ok": True}

    mapped = []
    for entry in iterable:
        if isinstance(entry, dict):
            mapped.append(dict(entry))
        else:
            mapped.append({"message": str(entry)})

    if not mapped:
        return {"ok": True}
    if len(mapped) == 1:
        store.append_log(mapped[0])
        _mirror_entry(mapped[0])
    else:
        store.extend_logs(mapped)
        for entry in mapped:
            _mirror_entry(entry)
    return {"ok": True}


__all__ = ["bridge_router", "set_store"]
