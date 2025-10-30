from __future__ import annotations

import logging
import math
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from .state import ControllerState

try:
    from app.db.models.MzPoliShineDB import CuttingStatusTable, StatusTable
except Exception:  # pragma: no cover - optional dependency path
    StatusTable = None  # type: ignore[assignment]
    CuttingStatusTable = None

LOG = logging.getLogger("controller.http.status")


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
        filtered = "".join(ch for ch in value if ch.isdigit() or ch in {",", ".", "-"})
        normalised = filtered.replace(",,", ",")
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
        torque_raw = self._to_float(getattr(row, "torque", None))
        torque_value = round(torque_raw, 3) if torque_raw is not None else None
        series_b_value = torque_value if torque_value is not None else (round(temperature, 3) if temperature else 0.0)

        position = self._parse_xyz(row.p_relative_position)

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
            "spindle_torque": torque_value or 0.0,
            "feed_rate": round(feed_rate, 3),
            "travel_speed": round(motion_speed, 3),
            "statusLights": lights,
            "lightStates": lights,
            "lights": lights,
            "position": position,
            "seriesA": spindle_rpm,
            "seriesB": series_b_value,
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
        row_data = getattr(row, "data", None)
        if isinstance(row_data, dict):
            payload["data"] = dict(row_data)
            torque_max_candidate = self._to_float(row_data.get("torque_max"))
            if torque_max_candidate is not None:
                payload.setdefault("torque_max", round(torque_max_candidate, 3))
        self._apply_runner_health(row=row, payload=payload)
        return payload

    def _fetch_status(self, session: Session) -> Optional[StatusTable]:
        stmt = select(StatusTable).limit(1)
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def _fetch_cutting(self, session: Session):
        if CuttingStatusTable is None:
            return None
        stmt = select(CuttingStatusTable).limit(1)
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
                    torque=Decimal("0.000"),
                    s_spindle_speed=0,
                    s_feed_speed=0,
                    s_point_motion_speed=0,
                    status_time=datetime.utcnow(),
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow(),
                    data={},
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
            health["message"] = "Task runner heartbeat unknown"
            health["alert_key"] = alert_key
            self._emit_runner_alert(payload, health, alert_key)
        elif lag > timeout:
            health["status"] = "error"
            health["message"] = f"Task runner offline (lag {lag:.1f}s)"
            health["alert_key"] = alert_key
            self._emit_runner_alert(payload, health, alert_key)
            payload["lights"]["controller"] = "FAULT"
            payload["lights"]["motion"] = "FAULT"
            payload["lights"]["device"] = "FAULT"
            payload["lights"]["spindle"] = "FAULT"
            payload["state"] = "offline"
        else:
            health["status"] = "ok"
            health["alert_key"] = None
            if self._runner_fault_active:
                health["recovered"] = True
            self._runner_fault_active = False
            self._last_runner_alert_key = None
        payload["task_runner_health"] = health

    def _emit_runner_alert(self, payload: Dict[str, Any], health: Dict[str, Any], alert_key: str) -> None:
        message = health.get("message") or "Task runner offline"
        alerts = payload.setdefault("alerts", [])
        if not any(alert.get("code") == alert_key for alert in alerts):
            alerts.append({"level": "error", "message": message, "code": alert_key})
        if not self._runner_fault_active or self._last_runner_alert_key != alert_key:
            self._runner_fault_active = True
            self._last_runner_alert_key = alert_key

    def build(self, state: ControllerState, timestamp: float, cycle: float) -> Dict[str, Any]:  # noqa: ARG002
        cutting_row = None
        try:
            with self._session_factory() as session:
                row = self._fetch_status(session)
                if CuttingStatusTable is not None:
                    cutting_row = self._fetch_cutting(session)
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to query StatusTable: {exc}") from exc
        if row is None:
            try:
                session.rollback()
            except Exception:
                pass
            self._ensure_default_row()
            with self._session_factory() as retry_session:
                row = self._fetch_status(retry_session)
                if CuttingStatusTable is not None:
                    cutting_row = self._fetch_cutting(retry_session)
            if row is None:
                raise RuntimeError("StatusTable currently has no records")

        payload = self._row_to_payload(row, timestamp=timestamp, label=state.label)
        if cutting_row is not None:
            rpm_val = self._to_float(getattr(cutting_row, "spindle_rpm", None))
            if rpm_val is not None:
                rpm_int = int(round(rpm_val))
                payload["seriesA"] = rpm_int
                if not payload.get("spindle_rpm"):
                    payload["spindle_rpm"] = rpm_int

        state.run_mode = payload.get("run_mode", state.run_mode)
        state.spindle_rpm = float(payload.get("spindle_rpm", state.spindle_rpm))
        return payload

    def close(self) -> None:
        if self._owns_engine:
            try:
                self._engine.dispose()
            except Exception:  # pragma: no cover - best effort cleanup
                pass


def read_cutting_payload(session_factory: sessionmaker) -> Dict[str, object]:
    if CuttingStatusTable is None:
        raise RuntimeError("CuttingStatusTable model unavailable; ensure database models are generated")

    with session_factory() as session:
        cutting_row = session.execute(select(CuttingStatusTable).limit(1)).scalar_one_or_none()
        status_row = None
        if StatusTable is not None:
            status_row = session.execute(select(StatusTable).limit(1)).scalar_one_or_none()

    if cutting_row is None:
        raise RuntimeError("CuttingStatusTable currently has no records")

    def _scalar(value: Optional[Any]) -> float:
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    feed = _scalar(getattr(cutting_row, "feed_rate", None))
    elapsed = _scalar(getattr(cutting_row, "elapsed_sec", None))
    spindle_rpm = _scalar(getattr(cutting_row, "spindle_rpm", None))
    torque = 0.0
    torque_max = 0.0
    if status_row is not None:
        torque = _scalar(getattr(status_row, "torque", None))
        torque_max = torque
        status_data = getattr(status_row, "data", None)
        if isinstance(status_data, dict):
            candidate = status_data.get("torque_max")
            if candidate is not None:
                torque_max = max(_scalar(candidate), torque)

    payload: Dict[str, object] = {
        "ts": time.time(),
        "feed_rate": round(feed, 3),
        "torque": round(torque, 3),
        "torque_max": round(torque_max, 3),
        "elapsed_sec": round(elapsed, 3),
    }
    if spindle_rpm:
        payload["spindle_rpm"] = round(spindle_rpm, 2)
    return payload


__all__ = [
    "StatusSourceProtocol",
    "SimulatedStatusSource",
    "DbStatusSource",
    "read_cutting_payload",
]
