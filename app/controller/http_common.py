from __future__ import annotations

import argparse
import asyncio
import logging
import math
import signal
import time
from dataclasses import dataclass, field
from decimal import Decimal
import json
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse
from uuid import uuid4

import requests
from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config import HTTP_BRIDGE_BASE, HTTP_CONTROL_ENDPOINT, HTTP_TIMEOUT
from app.controller.httpbridge import HttpControllerService
from app.common.tasks import TaskStatus, TaskType

try:
    from app.db.models.MzPoliShineDB import CuttingStatusTable, HardwareTaskQueue, StatusTable
except Exception:  # pragma: no cover - optional dependency path
    StatusTable = None  # type: ignore[assignment]
    CuttingStatusTable = None
    HardwareTaskQueue = None  # type: ignore[assignment]

LOG = logging.getLogger("controller.http")


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


class HttpBridgeFileLogger:
    """Append structured controller telemetry to date-partitioned log files."""

    def __init__(self, root: Path, *, encoding: str = "utf-8") -> None:
        self._root = Path(root)
        self._encoding = encoding
        self._root.mkdir(parents=True, exist_ok=True)

    def write(self, category: str, payload: Any, **extra: Any) -> None:
        entry: Dict[str, Any] = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "payload": payload,
        }
        if extra:
            entry.update(extra)
        self._append(category, entry)

    def write_many(self, category: str, payloads: Iterable[Any], **extra: Any) -> None:
        for item in payloads:
            self.write(category, item, **extra)

    def _append(self, category: str, entry: Dict[str, Any]) -> None:
        safe_category = category or "logs"
        category_dir = self._root / safe_category
        category_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now():%Y-%m-%d}.log"
        path = category_dir / filename
        with path.open("a", encoding=self._encoding) as fh:
            json.dump(entry, fh, ensure_ascii=False, default=_json_default)
            fh.write("\n")


@dataclass
class ControllerState:
    """Mutable controller state shared by simulator and production runners."""

    label: str = "http-controller"
    run_mode: str = "HTTP"
    spindle_rpm: float = 1200.0
    torque_bias: float = 0.3
    command_log: List[Dict[str, str]] = field(default_factory=list)
    program_lines: List[str] = field(
        default_factory=lambda: [
            "%",
            "O3000 (HTTP DEMO)",
            "G90 G21 G17",
            "G0 X0.000 Y0.000 Z5.000",
            "G1 X20.000 Y0.000 Z-0.200 F800.0",
            "G1 X20.000 Y20.000 Z-0.200",
            "G1 X0.000 Y20.000 Z-0.200",
            "G1 X0.000 Y0.000 Z-0.200",
            "G0 Z5.000",
            "M30",
        ]
    )
    program_current: int = -1
    program_running: bool = False
    _program_dirty: bool = True

    def register_command(self, action: str, ok: bool, message: str) -> None:
        self.command_log.append(
            {
                "ts": time.time(),
                "level": "INFO" if ok else "WARN",
                "name": "controller",
                "msg": f"control action={action} message={message}",
            }
        )

    def start_program(self) -> bool:
        if not self.program_lines:
            return False
        self.program_running = True
        self.program_current = -1
        self._program_dirty = True
        return True

    def stop_program(self) -> None:
        self.program_running = False
        self.program_current = -1
        self._program_dirty = True

    def advance_program(self) -> None:
        if not self.program_running or not self.program_lines:
            return
        self.program_current = (self.program_current + 1) % len(self.program_lines)
        self._program_dirty = True

    def mark_program_dirty(self) -> None:
        self._program_dirty = True

    def program_snapshot(self) -> Optional[Dict[str, object]]:
        if not self._program_dirty:
            return None
        self._program_dirty = False
        state_label = "RUNNING" if self.program_running else "IDLE"
        return {
            "program": list(self.program_lines),
            "program_state": {"state": state_label, "current": self.program_current},
        }


class StatusSourceProtocol:
    """Interface for status sources."""

    def build(self, state: ControllerState, timestamp: float, cycle: float) -> Dict[str, Any]:
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover - trivial
        return


class SimulatedStatusSource(StatusSourceProtocol):
    """Generate synthetic status snapshots."""

    def build(self, state: ControllerState, timestamp: float, cycle: float) -> Dict[str, Any]:
        spindle = state.spindle_rpm + 40.0 * math.sin(cycle * 0.3)
        torque = state.torque_bias + 0.1 * abs(math.sin(cycle * 0.5))
        x = 120.0 + 2.0 * math.sin(cycle * 0.2)
        y = 60.0 + 1.5 * math.sin(cycle * 0.17)
        z = -0.4 + 0.05 * math.cos(cycle * 0.11)
        theta = math.degrees(math.sin(cycle * 0.07)) * 0.5

        return {
            "label": state.label,
            "ts": timestamp,
            "state": "RUNNING" if state.program_running else "IDLE",
            "run_mode": state.run_mode,
            "serial_number": f"SIM-{int(timestamp)}",
            "spindle_rpm": round(spindle, 2),
            "spindle_torque": round(torque, 3),
            "position": {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "theta": round(theta, 3)},
            "statusLights": {
                "controller": "READY",
                "server": True,
                "spindle": "RUNNING" if spindle > 1100 else "READY",
                "motion": "RUNNING",
            },
        }


class DbStatusSource(StatusSourceProtocol):
    """Pull machine status from MzPoliShineDB.StatusTable."""

    RUN_STATE_MAP: Dict[int, tuple[str, str]] = {
        0: ("IDLE", "READY"),
        1: ("READY", "READY"),
        2: ("RUNNING", "RUNNING"),
        3: ("PAUSED", "WARNING"),
        4: ("STOPPED", "FAULT"),
    }
    CONTROL_MODE_MAP: Dict[int, str] = {0: "LOCAL", 1: "REMOTE"}
    MACHINE_MODE_MAP: Dict[int, str] = {
        0: "MANUAL",
        1: "AUTO",
        2: "SEMI_AUTO",
        3: "DEBUG",
        4: "MAINTENANCE",
    }

    def __init__(self, db_url: str, *, engine: Optional[Engine] = None) -> None:
        if StatusTable is None:
            raise RuntimeError("StatusTable model unavailable; ensure database models are generated")
        self._owns_engine = engine is None
        connect_args: Dict[str, Any] = {}
        if db_url.startswith("mysql"):
            connect_args["connect_timeout"] = 3
        self._engine = engine or create_engine(
            db_url,
            future=True,
            pool_pre_ping=True,
            pool_recycle=1800,
            connect_args=connect_args,
        )
        self._session_factory = sessionmaker(bind=self._engine, future=True, expire_on_commit=False)
        LOG.info("DB status source connected to %s", self._mask_password(db_url))
        self._ensure_default_row()
        self._runner_timeout = 10.0
        self._runner_fault_active = False
        self._last_runner_alert_key: Optional[str] = None

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        return self._session_factory

    @staticmethod
    def _mask_password(url: str) -> str:
        try:
            scheme, rest = url.split("://", 1)
        except ValueError:
            return url
        if "@" not in rest:
            return url
        creds, location = rest.split("@", 1)
        if ":" not in creds:
            return url
        user = creds.split(":", 1)[0]
        return f"{scheme}://{user}:***@{location}"

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, Decimal):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_xyz(value: Optional[str]) -> Dict[str, float]:
        default = {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0}
        if not value:
            return default
        normalised = value.replace("，", ",")
        parts = [p.strip() for p in normalised.split(",") if p.strip()]
        if len(parts) < 3:
            return default
        try:
            x_val, y_val, z_val = (float(parts[0]), float(parts[1]), float(parts[2]))
        except ValueError:
            return default
        return {"x": round(x_val, 3), "y": round(y_val, 3), "z": round(z_val, 3), "theta": 0.0}

    def _row_to_payload(self, row: StatusTable, *, timestamp: float, label: str) -> Dict[str, Any]:
        state_name, light_state = self.RUN_STATE_MAP.get(row.c_run_status, ("UNKNOWN", "READY"))
        control_mode = self.CONTROL_MODE_MAP.get(row.c_control_mode, f"MODE_{row.c_control_mode}")
        machine_mode = self.MACHINE_MODE_MAP.get(row.c_machine_mode, f"MODE_{row.c_machine_mode}")

        spindle_rpm = int(row.s_spindle_speed or 0)
        feed_rate = self._to_float(row.s_feed_speed) or 0.0
        motion_speed = self._to_float(row.s_point_motion_speed) or 0.0
        temperature = self._to_float(row.s_temperature)

        position = self._parse_xyz(row.p_absolute_position)

        lights = {
            "controller": "RUNNING",
            "server": True,
            "motion": light_state,
            "device": "FAULT" if row.c_alarm_status else light_state,
            "spindle": "FAULT" if row.c_alarm_status else ("RUNNING" if spindle_rpm > 0 else "READY"),
        }

        payload: Dict[str, Any] = {
            "label": label,
            "ts": timestamp,
            "state": state_name,
            "run_mode": control_mode,
            "machine_mode": machine_mode,
            "serial_number": f"MZ-{row.id}",
            "spindle_rpm": spindle_rpm,
            "spindle_torque": 0.0,
            "feed_rate": round(feed_rate, 3),
            "travel_speed": round(motion_speed, 3),
            "statusLights": lights,
            "lightStates": lights,
            "lights": lights,
            "position": position,
            "seriesA": spindle_rpm,
            "seriesB": temperature or 0.0,
            "control_mode_code": row.c_control_mode,
            "machine_mode_code": row.c_machine_mode,
            "alarm_active": bool(row.c_alarm_status),
        }
        payload["state_code"] = state_name
        payload["state_value"] = row.c_run_status

        if temperature is not None:
            payload["spindle_temperature"] = round(temperature, 2)
        if row.status_time:
            payload["status_time"] = row.status_time.isoformat()
        if row.c_alarm_status:
            payload["alerts"] = [{"level": "error", "message": "Alarm reported by StatusTable"}]

        metrics: Dict[str, Any] = {}
        for key in (
            "s_tool_diameter",
            "s_line_spacing",
            "s_total_cutting_depth",
            "s_clearance_speed",
            "s_work_surface_height",
            "s_cutting_depth",
            "s_step_distance",
        ):
            value = getattr(row, key, None)
            converted = self._to_float(value)
            if converted is not None:
                metrics[key] = converted
        if metrics:
            payload["metrics"] = metrics

        fixture_bits = getattr(row, "f_fixture_status", None)
        if fixture_bits is not None:
            payload["fixture_status_bits"] = int(fixture_bits)
        self._apply_runner_health(row=row, payload=payload)
        return payload

    def _fetch_status(self, session: Session) -> Optional[StatusTable]:
        stmt = select(StatusTable).limit(1)
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def _ensure_default_row(self) -> None:
        if StatusTable is None:
            return
        try:
            with self._session_factory() as session:
                row = self._fetch_status(session)
                if row is not None:
                    session.rollback()
                    return
                seed = StatusTable(  # type: ignore[call-arg]
                    id=1,
                    c_run_status=0,
                    c_alarm_status=0,
                    c_control_mode=0,
                    c_machine_mode=0,
                    s_spindle_speed=0,
                    s_feed_speed=0,
                    s_point_motion_speed=0,
                    status_time=datetime.utcnow(),
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow(),
                )
                session.add(seed)
                session.commit()
                LOG.info("Inserted default StatusTable row as seed entry")
        except Exception as exc:  # pragma: no cover - best effort bootstrap
            LOG.warning("Unable to seed StatusTable default row: %s", exc)

    def _apply_runner_health(self, *, row: StatusTable, payload: Dict[str, Any]) -> None:
        heartbeat = getattr(row, "updated_time", None) or getattr(row, "status_time", None)
        now_dt = datetime.utcnow()
        lag: Optional[float] = None
        if heartbeat is not None:
            heartbeat_dt = heartbeat
            try:
                if heartbeat_dt.tzinfo is not None:
                    heartbeat_dt = heartbeat_dt.astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                heartbeat_dt = heartbeat
            lag = max(0.0, (now_dt - heartbeat_dt).total_seconds())

        timeout = max(self._runner_timeout, 1.0)
        health: Dict[str, Any] = {
            "status": "unknown",
            "lag_seconds": round(lag, 3) if lag is not None else None,
            "last_heartbeat": heartbeat.isoformat() if heartbeat else None,
            "timeout_seconds": timeout,
        }
        alert_key = "task_runner_offline"

        if lag is None:
            health["status"] = "error"
            health["message"] = "任务执行程序心跳未知"
            health["alert_key"] = alert_key
            self._emit_runner_alert(payload, health, alert_key)
        elif lag > timeout:
            health["status"] = "error"
            health["message"] = f"任务执行程序已离线（延迟 {lag:.1f}s）"
            health["alert_key"] = alert_key
            self._emit_runner_alert(payload, health, alert_key)
            payload["lights"]["controller"] = "FAULT"
            payload["lights"]["motion"] = "FAULT"
            payload["lights"]["device"] = "FAULT"
            payload["lights"]["spindle"] = "FAULT"
            payload["state"] = "离线"
        else:
            health["status"] = "ok"
            health["alert_key"] = None
            if self._runner_fault_active:
                health["recovered"] = True
            self._runner_fault_active = False
            self._last_runner_alert_key = None
        payload["task_runner_health"] = health

    def _emit_runner_alert(self, payload: Dict[str, Any], health: Dict[str, Any], alert_key: str) -> None:
        message = health.get("message") or "任务执行程序已离线"
        alerts = payload.setdefault("alerts", [])
        if not any(alert.get("code") == alert_key for alert in alerts):
            alerts.append({"level": "error", "message": message, "code": alert_key})
        if not self._runner_fault_active or self._last_runner_alert_key != alert_key:
            self._runner_fault_active = True
            self._last_runner_alert_key = alert_key


    def build(self, state: ControllerState, timestamp: float, cycle: float) -> Dict[str, Any]:  # noqa: ARG002
        try:
            with self._session_factory() as session:
                row = self._fetch_status(session)
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to query StatusTable: {exc}") from exc
        if row is None:
            session.rollback()
            self._ensure_default_row()
            with self._session_factory() as retry_session:
                row = self._fetch_status(retry_session)
            if row is None:
                raise RuntimeError("StatusTable currently has no records")

        payload = self._row_to_payload(row, timestamp=timestamp, label=state.label)
        state.run_mode = payload.get("run_mode", state.run_mode)
        state.spindle_rpm = float(payload.get("spindle_rpm", state.spindle_rpm))
        return payload

    def close(self) -> None:
        if self._owns_engine:
            try:
                self._engine.dispose()
            except Exception:  # pragma: no cover - best effort cleanup
                pass


class TaskQueueWriter:
    """Persist control commands into HardwareTaskQueue."""

    ACTION_NAME_MAP: Dict[str, str] = {
        "capture": "采集",
        "start": "开始执行",
        "run.start": "开始执行",
        "run.stop": "停止执行",
        "stop": "停止执行",
        "estop": "急停",
        "reset": "复位",
        "motion.set_speed": "设置速度",
        "motion.set_work_origin": "设置工件原点",
        "motion.home": "回零",
        "motion.jog": "点动",
        "boost": "性能提升",
    }

    def __init__(self, session_factory: sessionmaker, *, engine: Optional[Engine] = None, owns_engine: bool = False) -> None:
        if HardwareTaskQueue is None:
            raise RuntimeError("HardwareTaskQueue model unavailable; cannot enqueue tasks.")
        self._session_factory = session_factory
        self._engine = engine
        self._owns_engine = owns_engine
        self._metadata = MetaData()
        self._task_table: Optional[Table] = None

    @classmethod
    def from_url(cls, db_url: str) -> "TaskQueueWriter":
        connect_args: Dict[str, Any] = {}
        if db_url.startswith("mysql"):
            connect_args["connect_timeout"] = 3
        engine = create_engine(db_url, future=True, pool_pre_ping=True, pool_recycle=1800, connect_args=connect_args)
        session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
        return cls(session_factory, engine=engine, owns_engine=True)

    def enqueue(self, *, task_type: str, device_id: str, params: Optional[Dict[str, Any]] = None, priority: int = 0) -> None:
        payload = {
            "task_id": uuid4().hex,
            "task_type": task_type,
            "device_id": device_id,
            "task_params": params or {},
            "priority": priority,
            "status": 0,
        }
        with self._session_factory() as session:
            entry = HardwareTaskQueue(**payload)  # type: ignore[arg-type]
            session.add(entry)
            session.commit()

    def _ensure_task_table(self, session: Session) -> Optional[Table]:
        if self._task_table is not None:
            return self._task_table
        try:
            self._task_table = Table("task_table", self._metadata, autoload_with=session.bind)
        except SQLAlchemyError as exc:
            LOG.error("Unable to reflect task_table: %s", exc)
            self._task_table = None
        return self._task_table

    @classmethod
    def _normalise_action(cls, action: str) -> str:
        return str(action or "").strip().lower()

    @classmethod
    def _friendly_action_name(cls, action: str) -> str:
        key = cls._normalise_action(action)
        return cls.ACTION_NAME_MAP.get(key, action or "鎺у埗鎸囦护")

    def log_control_task(
        self,
        *,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        workpiece_id: Optional[int] = None,
        record_id: Optional[int] = None,
    ) -> None:
        """Insert a task_table row describing the control command."""
        params = dict(params or {})
        now = time.time()
        action_key = self._normalise_action(action)
        action_name = self._friendly_action_name(action)
        with self._session_factory() as session:
            table = self._ensure_task_table(session)
            if table is None:
                return
            columns = table.c
            payload: Dict[str, Any] = {
                "t_task_name": f"control:{action_key or 'command'}",
                "t_task_type": int(TaskType.CONTROL),
            }
            if "t_status" in columns:
                payload["t_status"] = int(TaskStatus.PENDING)
            if "t_priority" in columns:
                payload["t_priority"] = 1
            if "t_progress" in columns:
                payload["t_progress"] = 0
            if "t_workpiece_id" in columns:
                payload["t_workpiece_id"] = workpiece_id
            if "t_record_id" in columns:
                payload["t_record_id"] = record_id
            if "t_payload" in columns:
                payload["t_payload"] = {
                    "action": action,
                    "action_key": action_key,
                    "action_name": action_name,
                    "params": params,
                    "queued_at": now,
                    "workpiece_id": workpiece_id,
                    "record_id": record_id,
                }
            if "t_status_detail" in columns:
                payload["t_status_detail"] = {
                    "source": "http_prod",
                    "state": "queued",
                    "updated_at": now,
                }
            try:
                result = session.execute(table.insert().values(**payload))
                session.commit()
                inserted_id = None
                if result and hasattr(result, "inserted_primary_key"):
                    pk = result.inserted_primary_key
                    if pk:
                        inserted_id = pk[0]
                LOG.info(
                    "Logged control task action=%s name=%s record=%s workpiece=%s task_id=%s",
                    action,
                    action_name,
                    record_id,
                    workpiece_id,
                    inserted_id,
                )
            except SQLAlchemyError as exc:
                session.rollback()
                LOG.error("Failed to log control task action=%s: %s", action, exc)

    def close(self) -> None:
        if self._owns_engine and self._engine is not None:
            try:
                self._engine.dispose()
            except Exception:
                pass


def _read_cutting_payload(session_factory: sessionmaker) -> Dict[str, object]:
    if CuttingStatusTable is None:
        raise RuntimeError("CuttingStatusTable model unavailable; ensure database models are generated")

    with session_factory() as session:
        row = session.execute(select(CuttingStatusTable).limit(1)).scalar_one_or_none()

    if row is None:
        raise RuntimeError("CuttingStatusTable currently has no records")

    def _scalar(value: Optional[Decimal | float | int]) -> float:
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    feed = _scalar(row.feed_rate)
    torque = _scalar(row.torque)
    elapsed = _scalar(row.elapsed_sec)
    spindle_rpm = _scalar(row.spindle_rpm)

    payload: Dict[str, object] = {
        "ts": time.time(),
        "feed_rate": round(feed, 3),
        "torque": round(torque, 3),
        "torque_max": round(torque, 3),
        "elapsed_sec": round(elapsed, 3),
    }
    if spindle_rpm:
        payload["spindle_rpm"] = round(spindle_rpm, 2)
    return payload


def _flush_command_logs(
    service: HttpControllerService,
    state: ControllerState,
    file_logger: Optional[HttpBridgeFileLogger] = None,
) -> int:
    if not state.command_log:
        return 0
    entries: List[Dict[str, object]] = list(state.command_log)
    state.command_log.clear()
    ok = False
    try:
        ok = service.publish_logs(entries)
    finally:
        if file_logger:
            file_logger.write_many(
                "control",
                ({**entry, "published": bool(ok)} for entry in entries),
            )
    return len(entries)


def _control_handler(state: ControllerState, task_writer: Optional[TaskQueueWriter], *, device_id: str):
    def _enqueue(task_type: str, params: Optional[Dict[str, Any]] = None, *, action: str, workpiece_id: Optional[int] = None, record_id: Optional[int] = None) -> None:
        if task_writer is None:
            return
        try:
            task_writer.enqueue(task_type=task_type, device_id=device_id, params=params)
            task_writer.log_control_task(action=action, params=params, workpiece_id=workpiece_id, record_id=record_id)
        except Exception as exc:
            LOG.error("Failed to enqueue hardware task %s: %s", task_type, exc)

    def _coerce_int(value: Any) -> Optional[int]:
        try:
            if value is None or value == "":
                return None
            candidate = int(value)
        except (TypeError, ValueError):
            return None
        return candidate

    def _resolve_identifiers(payload: Dict[str, object]) -> tuple[Optional[int], Optional[int]]:
        if not isinstance(payload, dict):
            return None, None
        record_candidates = (
            payload.get("record_id"),
            payload.get("recordId"),
            payload.get("record"),
        )
        workpiece_candidates = (
            payload.get("workpiece_id"),
            payload.get("workpieceId"),
            payload.get("workpiece"),
        )
        record_value = next((candidate for candidate in record_candidates if _coerce_int(candidate) is not None), None)
        workpiece_value = next((candidate for candidate in workpiece_candidates if _coerce_int(candidate) is not None), None)
        return _coerce_int(record_value), _coerce_int(workpiece_value)

    def handler(action: str, params: Dict[str, object]) -> Dict[str, object]:
        LOG.info("Control handler received action=%s params=%s", action, dict(params))
        normalized = action.strip().lower()
        if not normalized:
            state.register_command(action, False, "Empty action")
            return {"ok": False, "message": "Empty action"}

        record_id, workpiece_id = _resolve_identifiers(params or {})

        if normalized == "reset":
            state.spindle_rpm = 1100.0
            state.torque_bias = 0.2
            state.stop_program()
            state.register_command(action, True, "Reset acknowledged")
            _enqueue("RESET", {"action": action}, action=action, workpiece_id=workpiece_id, record_id=record_id)
            return {"ok": True, "message": "Reset acknowledged"}

        if normalized == "boost":
            state.spindle_rpm += 50.0
            state.torque_bias = min(state.torque_bias + 0.05, 0.6)
            state.register_command(action, True, "Boost applied")
            _enqueue("BOOST", {"action": action}, action=action, workpiece_id=workpiece_id, record_id=record_id)
            return {"ok": True, "message": "Boost applied"}

        if normalized in {"run.start", "start"}:
            if state.start_program():
                state.register_command(action, True, "Program playback started")
                _enqueue("POLISH_START", {"action": action, "params": dict(params)}, action=action, workpiece_id=workpiece_id, record_id=record_id)
                return {"ok": True, "message": "Program playback started"}
            state.register_command(action, False, "No program loaded")
            return {"ok": False, "message": "Program not available"}

        if normalized in {"run.stop", "stop"}:
            state.stop_program()
            state.register_command(action, True, "Program playback stopped")
            _enqueue("POLISH_STOP", {"action": action, "params": dict(params)}, action=action, workpiece_id=workpiece_id, record_id=record_id)
            return {"ok": True, "message": "Program playback stopped"}

        state.register_command(action, False, f"Unsupported action: {action}")
        _enqueue(normalized.upper(), {"action": action, "params": dict(params)}, action=action, workpiece_id=workpiece_id, record_id=record_id)
        return {"ok": False, "message": f"Unsupported action: {action}"}

    return handler


def build_parser(
    description: str,
    *,
    default_label: str,
    default_db_url: Optional[str] = None,
    default_device_id: str = "GRINDER-01",
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--label", default=default_label, help=f"Label field in status payloads (default: {default_label}).")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Interval between telemetry pushes in seconds (default: 1.0).",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=5,
        help="Publish a heartbeat log every N intervals (default: 5).",
    )
    parser.add_argument(
        "--http-base",
        default=HTTP_BRIDGE_BASE,
        help=f"HTTP bridge base URL exposed by the API server (default: {HTTP_BRIDGE_BASE}).",
    )
    parser.add_argument(
        "--http-control",
        default=HTTP_CONTROL_ENDPOINT,
        help=f"HTTP endpoint used by the API server to reach this controller (default: {HTTP_CONTROL_ENDPOINT}).",
    )
    parser.add_argument(
        "--http-timeout",
        type=float,
        default=HTTP_TIMEOUT,
        help=f"Timeout (seconds) for HTTP requests (default: {HTTP_TIMEOUT}).",
    )
    parser.add_argument(
        "--probe-bridge",
        action="store_true",
        help="Perform an initial GET /bridge/ping check before streaming telemetry.",
    )
    if default_db_url is not None:
        parser.add_argument(
            "--db-url",
            default=default_db_url,
            help=f"Database URL for StatusTable polling (default: {default_db_url}).",
        )
        parser.add_argument(
            "--disable-db",
            action="store_true",
            help="Ignore the configured database and emit purely simulated status data.",
        )
    parser.add_argument(
        "--device-id",
        default=default_device_id,
        help=f"Device identifier recorded in hardware task queue (default: {default_device_id}).",
    )
    return parser


def _parse_control_endpoint(url: str) -> tuple[str, int]:
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 9001
    return host, port


async def run_controller(
    args: argparse.Namespace,
    *,
    status_source: StatusSourceProtocol,
    fallback_source: Optional[StatusSourceProtocol] = None,
    task_writer: Optional[TaskQueueWriter] = None,
    task_runner: Optional[object] = None,
    file_logger: Optional[HttpBridgeFileLogger] = None,
) -> None:
    state = ControllerState(label=args.label)
    control_host, control_port = _parse_control_endpoint(args.http_control)
    LOG.info(
        "Controller starting (label=%s interval=%.2fs log_every=%d base=%s control=%s)",
        args.label,
        args.interval,
        args.log_every,
        args.http_base,
        args.http_control,
    )
    if getattr(args, "probe_bridge", False):
        try:
            resp = requests.get(f"{args.http_base.rstrip('/')}/ping", timeout=args.http_timeout)
            resp.raise_for_status()
        except requests.RequestException as exc:
            LOG.error("Bridge ping failed (%s): %s", args.http_base, exc)
        else:
            LOG.info("Bridge ping ok (%s)", args.http_base)

    service = HttpControllerService(
        base_url=args.http_base,
        control_host=control_host,
        control_port=control_port,
        timeout=args.http_timeout,
    )
    service.register_control_handler(_control_handler(state, task_writer, device_id=args.device_id))
    service.start()
    LOG.info("Control listener ready at http://%s:%s/control", control_host, control_port)

    session_factory = getattr(status_source, "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Status source does not expose session_factory; cutting telemetry requires database access.")

    stop_event = asyncio.Event()

    def _signal_handler(*_: Any) -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _signal_handler)
        except Exception:
            pass

    tick = 0
    try:
        while not stop_event.is_set():
            timestamp = time.time()
            cycle = tick * args.interval
            try:
                status_payload = status_source.build(state, timestamp, cycle)
            except Exception as exc:
                LOG.exception("Status build failed and fallback is disabled.")
                raise
            try:
                cutting_payload = _read_cutting_payload(session_factory)
            except Exception as exc:
                LOG.exception("Cutting payload build failed.")
                raise

            try:
                ok_status = service.publish_status(status_payload)
                LOG.info(
                    "Status push ok=%s rpm=%.2f",
                    ok_status,
                    status_payload.get("spindle_rpm", 0.0),
                )
                if file_logger:
                    file_logger.write("status", status_payload, ok=bool(ok_status))
            except Exception as exc:
                LOG.error("Status push failed: %s", exc)
                if file_logger:
                    file_logger.write("status", status_payload, ok=False, error=str(exc))
                await asyncio.sleep(args.interval)
                continue

            try:
                ok_cutting = service.publish_cutting(cutting_payload)
                LOG.info(
                    "Cutting push ok=%s feed=%.2f torque=%.3f elapsed=%.2f",
                    ok_cutting,
                    cutting_payload.get("feed_rate", 0.0),
                    cutting_payload.get("torque", 0.0),
                    cutting_payload.get("elapsed_sec", 0.0),
                )
                if file_logger:
                    file_logger.write("cutting", cutting_payload, ok=bool(ok_cutting))
            except Exception as exc:
                LOG.error("Cutting push failed: %s", exc)
                if file_logger:
                    file_logger.write("cutting", cutting_payload, ok=False, error=str(exc))
                await asyncio.sleep(args.interval)
                continue

            if state.program_running:
                state.advance_program()
            program_snapshot = state.program_snapshot()
            if program_snapshot is not None:
                try:
                    ok_program = service.publish_program(program_snapshot)
                    LOG.info("Program push ok=%s current=%s", ok_program, program_snapshot["program_state"].get("current"))
                    if file_logger:
                        file_logger.write("program", program_snapshot, ok=bool(ok_program))
                except Exception as exc:
                    LOG.error("Program push failed: %s", exc)
                    if file_logger:
                        file_logger.write("program", program_snapshot, ok=False, error=str(exc))

            if tick % args.log_every == 0:
                log_entry = {
                    "ts": timestamp,
                    "level": "INFO",
                    "name": "controller.sim",
                    "msg": f"heartbeat cycle={tick}",
                }
                try:
                    ok_log = service.publish_logs([log_entry])
                    LOG.info("Heartbeat log push ok=%s cycle=%d", ok_log, tick)
                    if file_logger:
                        file_logger.write("logs", log_entry, ok=bool(ok_log))
                except Exception as exc:
                    LOG.error("Heartbeat log push failed: %s", exc)
                    if file_logger:
                        file_logger.write("logs", log_entry, ok=False, error=str(exc))

            try:
                flushed = _flush_command_logs(service, state, file_logger=file_logger)
                if flushed:
                    LOG.info("Flushed %d control log entries", flushed)
            except Exception as exc:
                LOG.error("Control log flush failed: %s", exc)

            if task_runner is not None:
                try:
                    await asyncio.to_thread(task_runner.tick)
                except Exception as exc:
                    LOG.error("Task runner tick failed: %s", exc)

            tick += 1
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=args.interval)
            except asyncio.TimeoutError:
                continue
    finally:
        service.stop()
        close_builder = getattr(status_source, "close", None)
        if callable(close_builder):
            try:
                close_builder()
            except Exception:
                pass
        if task_writer is not None:
            task_writer.close()





