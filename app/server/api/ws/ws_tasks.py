from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from starlette.websockets import WebSocket, WebSocketDisconnect

from app.common.tasks import TaskStatus
from app.db import SessionLocal
from app.server.api.api.api_data import build_task_state_summary
from app.server.api.api_core import ws_router

log = logging.getLogger("app.ws")


def _parse_record_id(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _fetch_state(record_id: Optional[int]) -> Dict[str, Any]:
    with SessionLocal() as session:
        return build_task_state_summary(session=session, record_id=record_id)


def _fingerprint(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)


def _is_active(status: Any) -> bool:
    try:
        status_int = int(status)
    except (TypeError, ValueError):
        return False
    return status_int in (int(TaskStatus.PENDING), int(TaskStatus.RUNNING))


def _suggest_interval(payload: Dict[str, Any]) -> float:
    capture = payload.get("capture") or {}
    execute = payload.get("execute") or {}
    control = payload.get("control") or {}
    statuses = [capture.get("status"), execute.get("status"), control.get("status")]
    return 0.5 if any(_is_active(status) for status in statuses) else 2.0


@ws_router.websocket("/ws/tasks/state")
async def ws_tasks_state(ws: WebSocket):
    """任务队列状态 WebSocket：推送与 /data/tasks/state 同结构的汇总数据。"""
    await ws.accept()
    record_id = _parse_record_id(ws.query_params.get("record_id"))
    last_sent: Optional[str] = None
    try:
        try:
            log.info("WS connected endpoint=/ws/tasks/state client=%s", getattr(ws, "client", None))
        except Exception:
            pass

        while True:
            payload = await asyncio.to_thread(_fetch_state, record_id)
            fp = _fingerprint(payload)
            if fp != last_sent:
                await ws.send_json(payload)
                last_sent = fp
            await asyncio.sleep(_suggest_interval(payload))
    except WebSocketDisconnect:
        try:
            log.info("WS disconnected endpoint=/ws/tasks/state client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return

