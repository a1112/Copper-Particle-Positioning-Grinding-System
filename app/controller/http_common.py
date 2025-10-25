from __future__ import annotations

import argparse
import asyncio
import logging
import math
import signal
import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse
from uuid import uuid4

import requests
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config import HTTP_BRIDGE_BASE, HTTP_CONTROL_ENDPOINT, HTTP_TIMEOUT
from app.controller.httpbridge import HttpControllerService

try:
    from app.db.models.MzPoliShineDB import HardwareTaskQueue, StatusTable
except Exception:  # pragma: no cover - optional dependency path
    StatusTable = None  # type: ignore[assignment]
    HardwareTaskQueue = None  # type: ignore[assignment]

LOG = logging.getLogger("controller.http")


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

        position = (
            self._parse_xyz(row.p_work_position)
            if row.p_work_position
            else self._parse_xyz(row.p_absolute_position)
        )

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
        return payload

    def _fetch_status(self, session: Session) -> Optional[StatusTable]:
        stmt = select(StatusTable).limit(1)
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def build(self, state: ControllerState, timestamp: float, cycle: float) -> Dict[str, Any]:  # noqa: ARG002
        try:
            with self._session_factory() as session:
                row = self._fetch_status(session)
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to query StatusTable: {exc}") from exc
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

    def __init__(self, session_factory: sessionmaker, *, engine: Optional[Engine] = None, owns_engine: bool = False) -> None:
        if HardwareTaskQueue is None:
            raise RuntimeError("HardwareTaskQueue model unavailable; cannot enqueue tasks.")
        self._session_factory = session_factory
        self._engine = engine
        self._owns_engine = owns_engine

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

    def close(self) -> None:
        if self._owns_engine and self._engine is not None:
            try:
                self._engine.dispose()
            except Exception:
                pass


def _build_cutting_payload(state: ControllerState, timestamp: float, cycle: float) -> Dict[str, object]:
    feed = 20.0 + 4.0 * math.sin(cycle * 0.33)
    downfeed_target = 0.75
    downfeed_current = downfeed_target * (0.5 + 0.5 * (1 + math.sin(cycle * 0.1)) / 2)
    removal_expected = 120.0
    removal_current = removal_expected * (0.3 + 0.2 * (1 + math.sin(cycle * 0.08)))
    torque = state.torque_bias + 0.12 * abs(math.sin(cycle * 0.55))

    return {
        "ts": timestamp,
        "feed_rate": round(feed, 3),
        "downfeed_target": round(downfeed_target, 3),
        "downfeed_current": round(downfeed_current, 3),
        "removal_current": round(removal_current, 3),
        "removal_expected": round(removal_expected, 3),
        "torque_max": round(max(torque, state.torque_bias + 0.15), 3),
        "torque": round(torque, 3),
        "elapsed_sec": round(cycle, 2),
    }


def _flush_command_logs(service: HttpControllerService, state: ControllerState) -> int:
    if not state.command_log:
        return 0
    entries: List[Dict[str, object]] = list(state.command_log)
    state.command_log.clear()
    service.publish_logs(entries)
    return len(entries)


def _control_handler(state: ControllerState, task_writer: Optional[TaskQueueWriter], *, device_id: str):
    def _enqueue(task_type: str, params: Optional[Dict[str, Any]] = None) -> None:
        if task_writer is None:
            return
        try:
            task_writer.enqueue(task_type=task_type, device_id=device_id, params=params)
        except Exception as exc:
            LOG.error("Failed to enqueue hardware task %s: %s", task_type, exc)

    def handler(action: str, params: Dict[str, object]) -> Dict[str, object]:
        LOG.info("Control handler received action=%s params=%s", action, dict(params))
        normalized = action.strip().lower()
        if not normalized:
            state.register_command(action, False, "Empty action")
            return {"ok": False, "message": "Empty action"}

        if normalized == "reset":
            state.spindle_rpm = 1100.0
            state.torque_bias = 0.2
            state.stop_program()
            state.register_command(action, True, "Reset acknowledged")
            _enqueue("RESET", {"action": action})
            return {"ok": True, "message": "Reset acknowledged"}

        if normalized == "boost":
            state.spindle_rpm += 50.0
            state.torque_bias = min(state.torque_bias + 0.05, 0.6)
            state.register_command(action, True, "Boost applied")
            _enqueue("BOOST", {"action": action})
            return {"ok": True, "message": "Boost applied"}

        if normalized in {"run.start", "start"}:
            if state.start_program():
                state.register_command(action, True, "Program playback started")
                _enqueue("POLISH_START", {"action": action, "params": dict(params)})
                return {"ok": True, "message": "Program playback started"}
            state.register_command(action, False, "No program loaded")
            return {"ok": False, "message": "Program not available"}

        if normalized in {"run.stop", "stop"}:
            state.stop_program()
            state.register_command(action, True, "Program playback stopped")
            _enqueue("POLISH_STOP", {"action": action, "params": dict(params)})
            return {"ok": True, "message": "Program playback stopped"}

        state.register_command(action, False, f"Unsupported action: {action}")
        _enqueue(normalized.upper(), {"action": action, "params": dict(params)})
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
                LOG.error("Status build failed: %s", exc)
                if fallback_source is not None:
                    status_payload = fallback_source.build(state, timestamp, cycle)
                else:
                    await asyncio.sleep(args.interval)
                    continue
            cutting_payload = _build_cutting_payload(state, timestamp, cycle)

            try:
                ok_status = service.publish_status(status_payload)
                LOG.info(
                    "Status push ok=%s rpm=%.2f",
                    ok_status,
                    status_payload.get("spindle_rpm", 0.0),
                )
            except Exception as exc:
                LOG.error("Status push failed: %s", exc)
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
            except Exception as exc:
                LOG.error("Cutting push failed: %s", exc)
                await asyncio.sleep(args.interval)
                continue

            if state.program_running:
                state.advance_program()
            program_snapshot = state.program_snapshot()
            if program_snapshot is not None:
                try:
                    ok_program = service.publish_program(program_snapshot)
                    LOG.info("Program push ok=%s current=%s", ok_program, program_snapshot["program_state"].get("current"))
                except Exception as exc:
                    LOG.error("Program push failed: %s", exc)

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
                except Exception as exc:
                    LOG.error("Heartbeat log push failed: %s", exc)

            try:
                flushed = _flush_command_logs(service, state)
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
