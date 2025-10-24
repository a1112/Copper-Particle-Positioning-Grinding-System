from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body

from .store import HttpDataStore
from app.server.data import get_backend
from app.server.api.ws.code_bus import bus as code_bus
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


def _normalize_program_lines(source: Any) -> list[str]:
    if source is None:
        return []
    if isinstance(source, (bytes, bytearray)):
        text = source.decode("utf-8", errors="ignore")
        raw_lines = text.splitlines()
    elif isinstance(source, str):
        raw_lines = source.splitlines()
    else:
        try:
            iterator = list(source)
        except TypeError as exc:
            raise ValueError("Program must be a sequence of strings or a newline-delimited string") from exc
        raw_lines = iterator
    lines: list[str] = []
    for item in raw_lines:
        if item is None:
            continue
        text = str(item)
        # Preserve empty lines but normalise Windows newline endings
        if text.endswith("\r"):
            text = text[:-1]
        lines.append(text)
    return lines


@bridge_router.post("/controller")
async def push_controller_program(
    payload: Dict[str, Any] = Body(...),
    store: HttpDataStore = Depends(_require_store),
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Controller payload must be an object")

    program_source = payload.get("program")
    if program_source is None:
        program_source = payload.get("lines") or payload.get("gcode")
    try:
        program_lines = _normalize_program_lines(program_source)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    store.set_program(program_lines)

    state_payload: Dict[str, Any] = {}
    if isinstance(payload.get("program_state"), dict):
        state_payload.update(payload["program_state"])

    state_field = payload.get("state")
    if isinstance(state_field, dict):
        state_payload.update(state_field)
    elif isinstance(state_field, str) and state_field:
        state_payload["state"] = state_field

    if "current" not in state_payload and payload.get("current") is not None:
        state_payload["current"] = payload.get("current")

    store.set_program_state(state_payload)

    await code_bus.set_program(program_lines)
    if state_payload:
        state_name = str(state_payload.get("state", "")).strip() or "IDLE"
        current_value = state_payload.get("current", -1)
        try:
            current_index = int(current_value)
        except (TypeError, ValueError):
            current_index = -1
        await code_bus.set_state(state_name, current_index)

    log.debug(
        "Bridge controller program updated lines=%d state=%s current=%s",
        len(program_lines),
        state_payload.get("state"),
        state_payload.get("current"),
    )

    response: Dict[str, Any] = {"ok": True, "lines": len(program_lines)}
    if "state" in state_payload:
        response["state"] = state_payload.get("state")
    if "current" in state_payload:
        try:
            response["current"] = int(state_payload.get("current"))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            pass
    return response


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
