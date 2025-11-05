from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.common.task_actions import (
    ACTION_META as TASK_ACTION_META,
    DEFAULT_TASK_NAME as TASK_DEFAULT_NAME,
    DEFAULT_TASK_TYPE as TASK_DEFAULT_TYPE,
    friendly_action_name,
    friendly_action_type,
    get_action_meta,
    normalise_action,
)

try:
    from app.db.models.MzPoliShineDB import HardwareTaskQueue, RecordTable
except Exception:  # pragma: no cover - optional dependency path
    HardwareTaskQueue = None  # type: ignore[assignment]
    RecordTable = None  # type: ignore[assignment]

LOG = logging.getLogger("controller.http.tasks")


class TaskQueueWriter:
    """Persist control commands into HardwareTaskQueue."""

    DEFAULT_TASK_NAME = TASK_DEFAULT_NAME
    DEFAULT_TASK_TYPE = TASK_DEFAULT_TYPE
    DEFAULT_CREATED_BY = "http_prod"

    ACTION_META: Dict[str, tuple[str, int]] = TASK_ACTION_META

    def __init__(self, session_factory: sessionmaker, *, engine: Optional[Engine] = None, owns_engine: bool = False) -> None:
        if HardwareTaskQueue is None:
            raise RuntimeError("HardwareTaskQueue model unavailable; cannot enqueue tasks.")
        self._session_factory = session_factory
        self._engine = engine
        self._owns_engine = owns_engine
        self._metadata = MetaData()
        self._hardware_table: Optional[Table] = None

    @classmethod
    def from_url(cls, db_url: str) -> "TaskQueueWriter":
        connect_args: Dict[str, Any] = {}
        if db_url.startswith("mysql"):
            connect_args["connect_timeout"] = 3
        engine = create_engine(db_url, future=True, pool_pre_ping=True, pool_recycle=1800, connect_args=connect_args)
        session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
        return cls(session_factory, engine=engine, owns_engine=True)

    def _ensure_hardware_table(self, session: Session) -> Optional[Table]:
        if self._hardware_table is not None:
            return self._hardware_table
        try:
            self._hardware_table = Table("hardware_task_queue", self._metadata, autoload_with=session.bind)
        except SQLAlchemyError as exc:
            LOG.error("Unable to reflect hardware_task_queue: %s", exc)
            self._hardware_table = None
        return self._hardware_table

    @classmethod
    def _normalise_action(cls, action: str) -> str:
        return normalise_action(action)

    @classmethod
    def _friendly_action_name(cls, action: str) -> str:
        return friendly_action_name(action)

    @classmethod
    def _friendly_action_type(cls, action: str) -> int:
        return friendly_action_type(action)

    @classmethod
    def _action_meta(cls, action: str) -> tuple[str, int]:
        return get_action_meta(action)

    def _resolve_record_id(self, session: Session, explicit: Optional[int]) -> Optional[int]:
        if explicit is not None:
            return explicit
        if RecordTable is None:
            return None
        try:
            latest = session.execute(
                select(RecordTable.id).order_by(RecordTable.id.desc()).limit(1)  # type: ignore[arg-type]
            ).scalar_one_or_none()
        except SQLAlchemyError:
            return None
        return latest

    def enqueue_control_action(
        self,
        *,
        action: str,
        device_id: str,
        params: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        status: int = 0,
        created_by: Optional[str] = None,
        task_name_override: Optional[str] = None,
        task_type_override: Optional[int] = None,
        workpiece_id: Optional[int] = None,
        record_id: Optional[int] = None,
    ) -> None:
        if HardwareTaskQueue is None:
            raise RuntimeError("HardwareTaskQueue model unavailable; cannot enqueue tasks.")
        params = dict(params or {})
        normalized = self._normalise_action(action)
        name_default, type_default = self._action_meta(normalized)
        task_name = task_name_override or name_default
        task_type = task_type_override if task_type_override is not None else type_default

        payload_params: Dict[str, Any] = {
            "action": action,
            "params": params,
            "task_name": task_name,
            "queued_at": time.time(),
        }
        if workpiece_id is not None:
            payload_params["workpiece_id"] = workpiece_id
        payload_params["action_key"] = normalized

        with self._session_factory() as session:
            table = self._ensure_hardware_table(session)
            if table is None:
                return
            resolved_record_id = self._resolve_record_id(session, record_id)
            if resolved_record_id is not None:
                payload_params.setdefault("record_id", resolved_record_id)
            payload_params.setdefault("device_id", device_id)
            columns = table.c

            def _coerce_device(value: str) -> Any:
                if "device_id" not in columns:
                    return value
                try:
                    python_type = columns["device_id"].type.python_type  # type: ignore[attr-defined]
                except Exception:
                    return value
                if python_type is int:
                    numeric = "".join(ch for ch in str(value) if ch.isdigit())
                    if numeric:
                        try:
                            return int(numeric)
                        except (TypeError, ValueError):
                            return 0
                    return 0
                return value

            now = datetime.now()
            row: Dict[str, Any] = {}

            def _assign(column: str, value: Any) -> None:
                if column not in columns:
                    return
                row[column] = value

            if resolved_record_id is not None:
                _assign("record_id", resolved_record_id)
            _assign("task_name", task_name)
            _assign("task_type", task_type)
            _assign("device_id", _coerce_device(device_id))
            _assign("task_params", payload_params)
            _assign("priority", priority)
            _assign("status", status)
            if "status_params" in columns:
                row["status_params"] = {"source": created_by or self.DEFAULT_CREATED_BY, "state": "queued"}
            if "created_by" in columns:
                row["created_by"] = created_by or self.DEFAULT_CREATED_BY
            if "created_time" in columns:
                row["created_time"] = now

            if not row:
                LOG.warning("No valid columns to insert for hardware task; action=%s", action)
                return

            try:
                result = session.execute(table.insert().values(**row))
                session.commit()
                inserted_id = None
                if result and hasattr(result, "inserted_primary_key"):
                    pk = result.inserted_primary_key
                    if pk:
                        inserted_id = pk[0]
                LOG.info(
                    "Enqueued hardware task action=%s name=%s type=%s device=%s record=%s id=%s",
                    action,
                    task_name,
                    task_type,
                    device_id,
                    resolved_record_id,
                    inserted_id,
                )
            except SQLAlchemyError as exc:
                LOG.error("Failed to enqueue hardware task action=%s: %s", action, exc)

    def enqueue(
        self,
        *,
        task_type: str,
        device_id: str,
        params: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        created_by: str = DEFAULT_CREATED_BY,
    ) -> None:
        """Backward-compatible API used by the demo runner (task_type interpreted as action key)."""
        action = task_type
        self.enqueue_control_action(
            action=action,
            device_id=device_id,
            params=params,
            priority=priority,
            created_by=created_by,
        )

    def close(self) -> None:
        if self._owns_engine and self._engine is not None:
            try:
                self._engine.dispose()
            except Exception:
                pass


__all__ = ["TaskQueueWriter"]
