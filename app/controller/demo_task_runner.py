from __future__ import annotations

import argparse
import logging
import math
import shutil
import time
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import config as APP_CONFIG
from app.common import save_data
from app.common.tasks import ControlInstruction, TaskStatus, TaskType
from app.common.task_actions import friendly_action_name, friendly_action_type, normalise_action
from app.controller.http_common import program
from app.db.models.MzPoliShineDB import (
    CuttingStatusTable,
    HardwareTaskQueue,
    RecordTable,
    StatusTable,
    WorkpieceTable,
)


LOG = logging.getLogger("controller.demo_task_runner")


class DemoTaskRunner:
    """Lightweight orchestrator that simulates capture/execute workflows for demos."""

    def __init__(
        self,
        session_factory: sessionmaker,
        *,
        save_dir: Path,
        task_writer: Optional[object] = None,
    ) -> None:
        self._session_factory = session_factory
        self._save_dir = save_dir
        self._task_writer = task_writer
        self._capture_duration = 10.0
        self._control_duration = 1.0
        self._execute_duration = 3.5
        self._default_device_id = 1
        self._sample_images: Dict[str, Path] = self._discover_samples()
        self._heartbeat_counter = 0
        self._sim_elapsed = 0.0
        self._last_metrics_timestamp = time.perf_counter()

    # ------------------------------------------------------------------ public

    def tick(self) -> None:
        """Advance demo tasks by one step."""
        self._save_dir.mkdir(parents=True, exist_ok=True)
        with self._session_factory() as session:
            changed = False
            changed |= self._ensure_status_mode(session)
            changed |= self._ensure_cutting_status(session)
            changed |= self._ensure_workpiece(session)
            changed |= self._advance_capture(session)
            changed |= self._advance_control(session)
            changed |= self._advance_execute(session)
            metrics = self._simulate_operational_metrics()
            changed |= self._heartbeat_status_table(session, metrics)
            changed |= self._heartbeat_cutting_status(session, metrics)
            if changed:
                session.commit()

    # ---------------------------------------------------------------- helpers

    def _ensure_workpiece(self, session: Session) -> bool:
        row = session.execute(select(WorkpieceTable).limit(1)).scalar_one_or_none()
        if row:
            return False
        workpiece = WorkpieceTable(
            w_workpiece_id="WP-DEMO-0001",
            w_workpiece_type="DEMO",
            w_material="Copper",
            w_dimensions="100x100x10",
            w_surface_requirement="Ra <= 0.2",
            w_status=0,
        )
        session.add(workpiece)
        return True

    def _ensure_status_mode(self, session: Session) -> bool:
        if StatusTable is None:
            return False
        row = session.execute(select(StatusTable).limit(1)).scalar_one_or_none()
        changed = False
        if row is None:
            row = StatusTable(  # type: ignore[call-arg]
                id=1,
                c_run_status=1,
                c_alarm_status=0,
                c_control_mode=1,
                c_machine_mode=1,
                status_time=datetime.utcnow(),
            )
            session.add(row)
            changed = True
            LOG.info("StatusTable seeded with REMOTE control mode (id=1).")
        else:
            if row.c_control_mode != 1:
                row.c_control_mode = 1
                changed = True
                LOG.info("StatusTable control_mode -> REMOTE")
            if row.c_run_status is None or row.c_run_status == 0:
                row.c_run_status = 1
                changed = True
                LOG.info("StatusTable run_status -> READY")
            if changed:
                row.status_time = datetime.utcnow()
        return changed

    def _ensure_cutting_status(self, session: Session) -> bool:
        if CuttingStatusTable is None:
            return False
        row = session.execute(select(CuttingStatusTable).limit(1)).scalar_one_or_none()
        if row:
            return False
        record = CuttingStatusTable(  # type: ignore[call-arg]
            id=1,
            feed_rate=Decimal("0.000"),
            elapsed_sec=Decimal("0.000"),
            spindle_rpm=Decimal("0.00"),
        )
        session.add(record)
        LOG.info("CuttingStatusTable seeded with demo defaults (id=1).")
        return True

    def _advance_capture(self, session: Session) -> bool:
        stmt = (
            select(HardwareTaskQueue)
            .where(HardwareTaskQueue.task_type == int(TaskType.CAPTURE))
            .where(HardwareTaskQueue.status.in_([int(TaskStatus.PENDING), int(TaskStatus.RUNNING)]))
            .order_by(HardwareTaskQueue.id.asc())
        )
        tasks: Iterable[HardwareTaskQueue] = session.scalars(stmt).all()
        changed = False
        latest_record_id = 0
        latest_task_id = 0
        if tasks:
            latest_record_id = max(int(task.record_id or 0) for task in tasks)
            if latest_record_id <= 0:
                latest_task_id = max(task.id for task in tasks if task.id is not None)
        for task in tasks:
            record_id = int(task.record_id or 0)
            if latest_record_id > 0:
                if record_id != latest_record_id:
                    continue
            elif latest_task_id and task.id != latest_task_id:
                continue
            detail = dict(task.status_params or {})
            now = time.time()
            status_pending = task.status == int(TaskStatus.PENDING)
            status_running = task.status == int(TaskStatus.RUNNING)
            if status_pending:
                detail["phase"] = "capturing"
                detail["started_at"] = now
                detail["updated_at"] = now
                detail["deadline"] = now + self._capture_duration
                task.status = int(TaskStatus.RUNNING)
                task.status_params = detail
                self._mark_record_stage(session, task.record_id, "capture_running")
                self._update_status_table(session, run_status=2, machine_mode=2)
                LOG.info(
                    "Capture task started (task_id=%s record_id=%s workpiece=%s)",
                    task.id,
                    task.record_id,
                    task.workpiece_id,
                )
                changed = True
                continue

            if status_running:
                deadline = float(detail.get("deadline", 0.0))
                if not deadline:
                    started_at = float(detail.get("started_at", now))
                    deadline = started_at + self._capture_duration
                    detail["deadline"] = deadline
                    task.status_params = detail
                    changed = True
                if now < deadline:
                    if detail.get("updated_at", 0.0) != now:
                        detail["updated_at"] = now
                        task.status_params = detail
                        changed = True
                    continue

            self._complete_capture_task(session, task, detail)
            changed = True
        return changed

    def _advance_control(self, session: Session) -> bool:
        stmt = (
            select(HardwareTaskQueue)
            .where(HardwareTaskQueue.task_type == int(TaskType.CONTROL))
            .where(HardwareTaskQueue.status.in_([int(TaskStatus.PENDING), int(TaskStatus.RUNNING)]))
            .order_by(HardwareTaskQueue.id.asc())
        )
        tasks: Iterable[HardwareTaskQueue] = session.scalars(stmt).all()
        changed = False
        for task in tasks:
            detail = dict(task.status_params or {})
            now = time.time()
            if task.status == int(TaskStatus.PENDING):
                detail["phase"] = "control"
                detail["started_at"] = now
                detail["updated_at"] = now
                task.status = int(TaskStatus.RUNNING)
                task.status_params = detail
                self._update_status_table(session, run_status=2, machine_mode=3)
                LOG.info(
                    "Control task running (task_id=%s record_id=%s)",
                        task.id,
                    task.record_id,
                )
                changed = True
                continue
            started_at = float(detail.get("started_at", 0.0))
            if started_at and now - started_at < self._control_duration:
                if detail.get("updated_at", 0.0) != now:
                    detail["updated_at"] = now
                    task.status_params = detail
                    changed = True
                continue
            self._complete_control_task(session, task, detail)
            changed = True
        return changed

    def _advance_execute(self, session: Session) -> bool:
        stmt = (
            select(HardwareTaskQueue)
            .where(HardwareTaskQueue.task_type == int(TaskType.EXECUTE))
            .where(HardwareTaskQueue.status.in_([int(TaskStatus.PENDING), int(TaskStatus.RUNNING)]))
            .order_by(HardwareTaskQueue.id.asc())
        )
        tasks: Iterable[HardwareTaskQueue] = session.scalars(stmt).all()
        changed = False
        for task in tasks:
            detail = dict(task.status_params or {})
            now = time.time()
            if task.status == int(TaskStatus.PENDING):
                detail["phase"] = "execute"
                detail["started_at"] = now
                detail["updated_at"] = now
                task.status = int(TaskStatus.RUNNING)
                task.status_params = detail
                self._update_status_table(session, run_status=2, machine_mode=4)
                self._mark_record_stage(session, task.record_id, "execute_running")
                LOG.info(
                    "Execute task running (task_id=%s record_id=%s)",
                    task.id,
                    task.record_id,
                )
                changed = True
                continue
            started_at = float(detail.get("started_at", 0.0))
            if started_at and now - started_at < self._execute_duration:
                if detail.get("updated_at", 0.0) != now:
                    detail["updated_at"] = now
                    task.status_params = detail
                    changed = True
                continue
            self._complete_execute_task(session, task, detail)
            changed = True
        return changed

    # -------------------------------------------------------------- transitions

    def _complete_capture_task(self, session: Session, task: HardwareTaskQueue, detail: dict) -> None:
        record = session.get(RecordTable, task.record_id)
        commands: List[dict] = []
        artifact_folder: Optional[str] = None
        if record:
            artifact_folder = str((APP_CONFIG.SAVE_DATA_ROOT / "record" / str(record.id)).resolve())
            folder = save_data.ensure_record_folder(int(record.id))
            save_data.copy_current_artifacts(folder)
            alg_path, alg_json = save_data.copy_alg_result(folder)
            program_payload: Optional[Dict[str, Any]] = None
            if alg_json:
                try:
                    program_payload = program.build_program_payload_from_alg_data(alg_json)
                except Exception as exc:  # pragma: no cover - defensive
                    LOG.warning("Failed to build program payload for record %s: %s", record.id, exc)
            if program_payload:
                commands = program_payload.get("commands", [])
                camera_matrix = program_payload.get("camera_to_robot_matrix")
                if camera_matrix:
                    camera_data = dict(record.r_camera_data or {})
                    camera_data["camera_to_robot_matrix"] = camera_matrix
                else:
                    camera_data = dict(record.r_camera_data or {})
                camera_data.update(
                    {
                        "frames": 120,
                        "exposure_ms": 12.5,
                        "pending_copy": False,
                        "image_dir": artifact_folder,
                        "image_files": [],
                    }
                )
                record.r_camera_data = camera_data
                if program_payload.get("fixtures"):
                    warning_data = dict(record.r_warning_data or {})
                    warning_data["fixtures"] = program_payload["fixtures"]
                    record.r_warning_data = warning_data
            else:
                record.r_camera_data = {
                    "frames": 120,
                    "exposure_ms": 12.5,
                    "pending_copy": True,
                    "image_dir": None,
                    "image_files": [],
                }
            record.r_progress_data = {"stage": "capture_completed", "timestamp": time.time()}
            record.r_warning_data = record.r_warning_data or {
                "level": "info",
                "message": "Demo capture pipeline finished",
            }
        detail["phase"] = "completed"
        detail.pop("deadline", None)
        detail["finished_at"] = time.time()
        detail["updated_at"] = time.time()
        task.status = int(TaskStatus.COMPLETED)
        task.status_params = detail
        self._update_status_table(session, run_status=1, machine_mode=2)
        LOG.info(
            "Capture task completed (task_id=%s record_id=%s artifact_folder=%s)",
            task.id,
            task.record_id,
            artifact_folder,
        )

        control_exists = session.execute(
            select(HardwareTaskQueue)
            .where(HardwareTaskQueue.task_type == int(TaskType.CONTROL))
            .where(HardwareTaskQueue.record_id == task.record_id)
            .order_by(HardwareTaskQueue.id.desc())
        ).scalar_one_or_none()
        if control_exists:
            return

        control_task = HardwareTaskQueue(
            task_name=f"control-{task.record_id}",
            task_type=int(TaskType.CONTROL),
            workpiece_id=task.workpiece_id,
            record_id=task.record_id,
            task_params={"commands": commands},
            status=int(TaskStatus.PENDING),
            status_params={"phase": "queued"},
            device_id=self._default_device_id,
        )
        session.add(control_task)
        LOG.info(
            "Control task created (task_id=%s source_task=%s record_id=%s commands=%d)",
            control_task.id,
            task.id,
            task.record_id,
            len(commands),
        )

    def _complete_control_task(self, session: Session, task: HardwareTaskQueue, detail: dict) -> None:
        detail["phase"] = "completed"
        detail["finished_at"] = time.time()
        detail["updated_at"] = time.time()
        task.status = int(TaskStatus.COMPLETED)
        task.status_params = detail
        payload = task.task_params or {}
        commands = payload.get("commands") if isinstance(payload, dict) else None
        if not isinstance(commands, list):
            commands = []
        if not commands:
            self._update_status_table(session, run_status=1, machine_mode=3)
            return
        for index, cmd in enumerate(commands, start=1):
            instruction = ControlInstruction(
                ex=float(cmd.get("ex", 0.0)),
                ey=float(cmd.get("ey", 0.0)),
                ez=float(cmd.get("ez", 0.0)),
                spindle_rpm=float(cmd.get("r", 0.0)),
                velocity=float(cmd.get("v", 0.0)),
            )
            self._enqueue_control_command(instruction, index=index, total=len(commands))
        self._update_status_table(session, run_status=1, machine_mode=3)
        LOG.info(
            "Control task completed (task_id=%s record_id=%s commands=%d)",
            task.id,
            task.record_id,
            len(commands),
        )

    def _complete_execute_task(self, session: Session, task: HardwareTaskQueue, detail: dict) -> None:
        detail["phase"] = "completed"
        detail["finished_at"] = time.time()
        detail["updated_at"] = time.time()
        task.status = int(TaskStatus.COMPLETED)
        task.status_params = detail
        self._update_status_table(session, run_status=1, machine_mode=1)
        self._mark_record_stage(session, task.record_id, "execute_completed")
        LOG.info(
            "Execute task completed (task_id=%s record_id=%s)",
            task.id,
            task.record_id,
        )

    # --------------------------------------------------------------- utilities

    def _enqueue_control_command(self, instruction: ControlInstruction, *, index: int, total: int) -> None:
        if self._task_writer is None:
            return
        try:
            self._task_writer.enqueue(
                task_type="CONTROL",
                device_id="GRINDER-01",
                params={
                    "sequence": index,
                    "total": total,
                    "command": instruction.as_command_string(),
                    "payload": instruction.as_dict(),
                },
            )
        except Exception:
            # Best effort only; demo mode can ignore enqueue failures.
            pass

    def _copy_sample_images(self, target_dir: Path) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for alias, source in self._sample_images.items():
            dest = target_dir / f"{alias}.png"
            try:
                shutil.copyfile(source, dest)
                LOG.debug("Copied sample image %s -> %s", source, dest)
            except FileNotFoundError:
                with dest.open("wb") as fh:
                    fh.write(b"")
                LOG.warning("Sample image missing (%s); created empty placeholder at %s", source, dest)
            result[alias] = str(dest)
        return result

    def _discover_samples(self) -> Dict[str, Path]:
        root = Path(__file__).resolve().parents[2] / "TestData" / "images"
        mapping = {
            "color": "0_IMG_Color.png",
            "gray": "0_IMG_Texture_8Bit.png",
            "depth": "1_ZTbRender.png",
            "normal": "1_NzRender.png",
        }
        samples: Dict[str, Path] = {}
        for key, filename in mapping.items():
            path = root / filename
            samples[key] = path
        return samples

    def _mark_record_stage(self, session: Session, record_id: Optional[int], stage: str) -> None:
        if not record_id:
            return
        record = session.get(RecordTable, record_id)
        if not record:
            return
        payload = dict(record.r_progress_data or {})
        payload["stage"] = stage
        payload["updated_at"] = time.time()
        record.r_progress_data = payload

    def _update_status_table(
        self,
        session: Optional[Session],
        *,
        run_status: Optional[int] = None,
        machine_mode: Optional[int] = None,
        alarm_status: Optional[int] = None,
    ) -> None:
        if StatusTable is None:
            return
        owns_session = False
        if session is None:
            session = self._session_factory()
            owns_session = True
        try:
            row = session.execute(select(StatusTable).limit(1)).scalar_one_or_none()
            if row is None:
                row = StatusTable(  # type: ignore[call-arg]
                    id=1,
                    c_run_status=run_status if run_status is not None else 1,
                    c_alarm_status=alarm_status if alarm_status is not None else 0,
                    c_control_mode=1,
                    c_machine_mode=machine_mode if machine_mode is not None else 1,
                    status_time=datetime.utcnow(),
                )
                session.add(row)
            else:
                if run_status is not None:
                    row.c_run_status = run_status
                if alarm_status is not None:
                    row.c_alarm_status = alarm_status
                if machine_mode is not None:
                    row.c_machine_mode = machine_mode
                row.c_control_mode = 1
                row.status_time = datetime.utcnow()
            if owns_session:
                session.commit()
        except Exception:
            pass
        finally:
            if owns_session:
                session.close()

    def _heartbeat_status_table(self, session: Session, metrics: dict[str, float]) -> bool:
        if StatusTable is None:
            return False
        row = session.execute(select(StatusTable).limit(1)).scalar_one_or_none()
        if row is None:
            return False
        previous_time = row.status_time
        new_time = datetime.utcnow()
        row.status_time = new_time
        row.c_control_mode = 1
        if row.c_run_status is None:
            row.c_run_status = 1
        row.s_spindle_speed = int(round(metrics["spindle_rpm"]))
        row.s_feed_speed = int(round(metrics["feed_rate"]))
        row.s_point_motion_speed = int(round(metrics["point_speed"]))
        row.torque = self._decimal(metrics["torque"], "0.000")
        row.p_relative_position = self._format_position(metrics["x"], metrics["y"], metrics["z"])
        row.p_relative_position = self._format_position(
            metrics["relative_x"],
            metrics["relative_y"],
            metrics["relative_z"],
        )
        row.p_work_position = self._format_position(
            metrics["work_x"],
            metrics["work_y"],
            metrics["work_z"],
        )
        row.p_remaining_distance = self._format_position(
            metrics["remaining_x"],
            metrics["remaining_y"],
            metrics["remaining_z"],
        )
        previous_time_str = previous_time.strftime("%Y-%m-%dT%H:%M:%S") if isinstance(previous_time, datetime) else "None"
        current_time_str = new_time.strftime("%Y-%m-%dT%H:%M:%S")
        LOG.info(
            (
                "StatusTable heartbeat -> run_status=%s alarm_status=%s control_mode=%s machine_mode=%s "
                "abs=%s rel=%s velocity=%.2f feed=%.2f rpm=%.2f torque=%.2f current=%s previous=%s"
            ),
            row.c_run_status,
            row.c_alarm_status,
            row.c_control_mode,
            row.c_machine_mode,
            row.p_absolute_position,
            row.p_relative_position,
            metrics["velocity"],
            metrics["feed_rate"],
            metrics["spindle_rpm"],
            metrics["torque"],
            current_time_str,
            previous_time_str,
        )
        current_data = getattr(row, "data", None)
        base_data = dict(current_data) if isinstance(current_data, dict) else {}
        torque_value = round(metrics["torque"], 3)
        torque_max = base_data.get("torque_max")
        if isinstance(torque_max, (int, float, Decimal)):
            torque_max = max(float(torque_max), torque_value)
        else:
            torque_max = torque_value
        base_data.update({"torque": torque_value, "torque_max": round(torque_max, 3)})
        row.data = base_data
        return True

    def _heartbeat_cutting_status(self, session: Session, metrics: dict[str, float]) -> bool:
        if CuttingStatusTable is None:
            return False
        row = session.execute(select(CuttingStatusTable).limit(1)).scalar_one_or_none()
        if row is None:
            return False
        row.feed_rate = self._decimal(metrics["feed_rate"], "0.000")
        row.elapsed_sec = self._decimal(metrics["elapsed"], "0.000")
        row.spindle_rpm = self._decimal(metrics["spindle_rpm"], "0.00")
        LOG.info(
            "CuttingStatusTable heartbeat -> feed=%.3f torque=%.3f rpm=%.2f elapsed=%.2f velocity=%.2f",
            metrics["feed_rate"],
            metrics["torque"],
            metrics["spindle_rpm"],
            metrics["elapsed"],
            metrics["velocity"],
        )
        return True

    def _simulate_operational_metrics(self) -> dict[str, float]:
        now = time.perf_counter()
        delta = max(now - self._last_metrics_timestamp, 0.05)
        self._last_metrics_timestamp = now
        self._sim_elapsed += delta
        cycle = self._heartbeat_counter
        self._heartbeat_counter += 1
        angle = (cycle % 360) * math.pi / 180.0
        sweep = angle * 1.2
        base_x = 120.0
        base_y = 85.0
        base_z = -0.35
        x = base_x + 15.0 * math.sin(angle)
        y = base_y + 12.0 * math.cos(angle * 0.8)
        z = base_z + 0.08 * math.sin(angle * 0.5)
        rel_x = x - base_x
        rel_y = y - base_y
        rel_z = z - base_z
        progress_ratio = (math.sin(angle) + 1.0) / 2.0
        remaining_x = 20.0 * (1.0 - progress_ratio)
        remaining_y = 10.0 * (1.0 - progress_ratio)
        remaining_z = 2.0 * (1.0 - progress_ratio)
        velocity = 18.0 + 4.5 * math.sin(sweep)
        feed_rate = 12.0 + 3.0 * math.cos(sweep)
        point_speed = 6.0 + 1.5 * math.sin(sweep * 0.7)
        spindle_rpm = 2000.0
        torque = 30.0 + 1.2 * math.sin(angle * 1.3)
        return {
            "tick": cycle,
            "x": x,
            "y": y,
            "z": z,
            "relative_x": rel_x,
            "relative_y": rel_y,
            "relative_z": rel_z,
            "work_x": x,
            "work_y": y,
            "work_z": z,
            "remaining_x": remaining_x,
            "remaining_y": remaining_y,
            "remaining_z": remaining_z,
            "velocity": velocity,
            "feed_rate": feed_rate,
            "point_speed": point_speed,
            "spindle_rpm": spindle_rpm,
            "torque": torque,
            "elapsed": self._sim_elapsed,
        }

    @staticmethod
    def _format_position(x: float, y: float, z: float) -> str:
        return f"{x:.3f},{y:.3f},{z:.3f}"

    @staticmethod
    def _decimal(value: float, pattern: str) -> Decimal:
        quantize_target = Decimal(pattern)
        return Decimal(str(value)).quantize(quantize_target, rounding=ROUND_HALF_UP)

    @staticmethod
    def _normalise_camera_matrix(raw: object) -> Optional[list[list[float]]]:
        if raw is None:
            return None
        if isinstance(raw, dict):
            if "data" in raw:
                raw = raw["data"]
            else:
                raw = list(raw.values())
        if not isinstance(raw, (list, tuple)):
            return None
        values: List[float] = []
        for item in raw:
            try:
                values.append(float(item))
            except (TypeError, ValueError):
                values.append(0.0)
        matrix: List[List[float]] = []
        if len(values) == 16:
            for row in range(4):
                matrix.append(values[row * 4:(row + 1) * 4])
        elif len(values) == 12:
            for row in range(3):
                matrix.append(values[row * 4:(row + 1) * 4])
        else:
            return None
        if matrix:
            if len(matrix) == 3:
                matrix.append([0.0, 0.0, 0.0, 1.0])
            while len(matrix) < 4:
                matrix.append([0.0, 0.0, 0.0, 0.0])
            for row in matrix:
                while len(row) < 4:
                    row.append(0.0)
            matrix[3][0] = 0.0
            matrix[3][1] = 0.0
            matrix[3][2] = 0.0
            matrix[3][3] = 1.0
        return matrix


def _parse_cli_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the DemoTaskRunner against a database for local testing.")
    parser.add_argument(
        "--db-url",
        default="mysql+pymysql://remote_user:123456@127.0.0.1/MzPoliShineDB?charset=utf8mb4",
        help="SQLAlchemy URL for the MzPoliShineDB database (default: %(default)s).",
    )
    parser.add_argument(
        "--save-dir",
        default=str(Path(APP_CONFIG.PROJECT_ROOT) / "SaveData"),
        help="Directory for generated capture artifacts (default: %(default)s).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds to sleep between tick iterations (default: %(default)s).",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=0,
        help="Number of tick iterations to run (0 means run indefinitely).",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _run_cli(argv: Optional[Iterable[str]] = None) -> None:
    args = _parse_cli_args(argv)
    from app.db.base import create_engine_ensuring_database

    engine = create_engine_ensuring_database(args.db_url)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    runner = DemoTaskRunner(session_factory, save_dir=Path(args.save_dir))
    tick_count = 0
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        logging.getLogger().setLevel(logging.INFO)
    LOG.info("DemoTaskRunner CLI starting (db=%s save_dir=%s ticks=%s interval=%.2fs)", args.db_url, args.save_dir, args.ticks or "∞", args.interval)
    try:
        while True:
            runner.tick()
            tick_count += 1
            LOG.debug("Tick #%d complete", tick_count)
            if args.ticks and tick_count >= args.ticks:
                break
            time.sleep(max(args.interval, 0.05))
    except KeyboardInterrupt:
        LOG.info("DemoTaskRunner interrupted by user after %d ticks", tick_count)
    finally:
        LOG.info("DemoTaskRunner shutting down")
        engine.dispose()


if __name__ == "__main__":
    _run_cli()
