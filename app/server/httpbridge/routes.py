from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from .store import HttpDataStore

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
async def push_status(payload: Dict[str, Any], store: HttpDataStore = Depends(_require_store)) -> Dict[str, Any]:
    store.update_status(payload or {})
    log.debug("Bridge status updated (keys=%s)", list(payload or {}).keys())
    return {"ok": True}


@bridge_router.post("/cutting")
async def push_cutting(payload: Dict[str, Any], store: HttpDataStore = Depends(_require_store)) -> Dict[str, Any]:
    store.update_cutting(payload or {})
    return {"ok": True}


@bridge_router.post("/logs")
async def push_logs(entries: Any, store: HttpDataStore = Depends(_require_store)) -> Dict[str, Any]:
    if isinstance(entries, dict):
        store.append_log(entries)
        return {"ok": True}

    iterable: Iterable[Any]
    if isinstance(entries, list):
        iterable = entries
    else:
        try:
            iterable = list(entries)
        except TypeError:
            store.append_log({"message": str(entries)})
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
    else:
        store.extend_logs(mapped)
    return {"ok": True}


__all__ = ["bridge_router", "set_store"]

