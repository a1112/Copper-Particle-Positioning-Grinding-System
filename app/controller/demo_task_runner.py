from __future__ import annotations

import argparse
import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app import config as APP_CONFIG
from app.common.tasks import ControlInstruction, TaskStatus, TaskType
from app.db.models.MzPoliShineDB import RecordTable, StatusTable, TaskTable, WorkpieceTable


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
        self._capture_duration = 2.0
        self._control_duration = 1.0
        self._execute_duration = 3.5
        self._sample_images: Dict[str, Path] = self._discover_samples()

    # ------------------------------------------------------------------ public

    def tick(self) -> None:
        """Advance demo tasks by one step."""
        self._save_dir.mkdir(parents=True, exist_ok=True)
        with self._session_factory() as session:
            changed = False
            changed |= self._ensure_status_mode(session)
            changed |= self._ensure_workpiece(session)
            changed |= self._advance_capture(session)
            changed |= self._advance_control(session)
            changed |= self._advance_execute(session)
            if changed:
                session.commit()
            else:
                session.rollback()

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

    def _advance_capture(self, session: Session) -> bool:
        stmt = (
            select(TaskTable)
            .where(TaskTable.t_task_type == int(TaskType.CAPTURE))
            .where(TaskTable.t_status.in_([int(TaskStatus.PENDING), int(TaskStatus.RUNNING)]))
            .order_by(TaskTable.id.asc())
        )
        tasks: Iterable[TaskTable] = session.scalars(stmt).all()
        changed = False
        for task in tasks:
            detail = dict(task.t_status_detail or {})
            now = time.time()
            if task.t_status == int(TaskStatus.PENDING):
                detail["phase"] = "capturing"
                detail["started_at"] = now
                task.t_status = int(TaskStatus.RUNNING)
                task.t_status_detail = detail
                self._mark_record_stage(session, task.t_record_id, "capture_running")
                self._update_status_table(session, run_status=2, machine_mode=2)
                LOG.info(
                    "Capture task started (task_id=%s record_id=%s workpiece=%s)",
                    task.id,
                    task.t_record_id,
                    task.t_workpiece_id,
                )
                changed = True
                continue
            started_at = float(detail.get("started_at", 0.0))
            if started_at and now - started_at < self._capture_duration:
                continue
            self._complete_capture_task(session, task, detail)
            changed = True
        return changed

    def _advance_control(self, session: Session) -> bool:
        stmt = (
            select(TaskTable)
            .where(TaskTable.t_task_type == int(TaskType.CONTROL))
            .where(TaskTable.t_status.in_([int(TaskStatus.PENDING), int(TaskStatus.RUNNING)]))
            .order_by(TaskTable.id.asc())
        )
        tasks: Iterable[TaskTable] = session.scalars(stmt).all()
        changed = False
        for task in tasks:
            detail = dict(task.t_status_detail or {})
            now = time.time()
            if task.t_status == int(TaskStatus.PENDING):
                detail["phase"] = "control"
                detail["started_at"] = now
                task.t_status = int(TaskStatus.RUNNING)
                task.t_status_detail = detail
                self._update_status_table(session, run_status=2, machine_mode=3)
                LOG.info(
                    "Control task running (task_id=%s record_id=%s)",
                    task.id,
                    task.t_record_id,
                )
                changed = True
                continue
            started_at = float(detail.get("started_at", 0.0))
            if started_at and now - started_at < self._control_duration:
                continue
            self._complete_control_task(session, task, detail)
            changed = True
        return changed

    def _advance_execute(self, session: Session) -> bool:
        stmt = (
            select(TaskTable)
            .where(TaskTable.t_task_type == int(TaskType.EXECUTE))
            .where(TaskTable.t_status.in_([int(TaskStatus.PENDING), int(TaskStatus.RUNNING)]))
            .order_by(TaskTable.id.asc())
        )
        tasks: Iterable[TaskTable] = session.scalars(stmt).all()
        changed = False
        for task in tasks:
            detail = dict(task.t_status_detail or {})
            now = time.time()
            if task.t_status == int(TaskStatus.PENDING):
                detail["phase"] = "execute"
                detail["started_at"] = now
                task.t_status = int(TaskStatus.RUNNING)
                task.t_status_detail = detail
                self._update_status_table(session, run_status=2, machine_mode=4)
                self._mark_record_stage(session, task.t_record_id, "execute_running")
                LOG.info(
                    "Execute task running (task_id=%s record_id=%s)",
                    task.id,
                    task.t_record_id,
                )
                changed = True
                continue
            started_at = float(detail.get("started_at", 0.0))
            if started_at and now - started_at < self._execute_duration:
                continue
            self._complete_execute_task(session, task, detail)
            changed = True
        return changed

    # -------------------------------------------------------------- transitions

    def _complete_capture_task(self, session: Session, task: TaskTable, detail: dict) -> None:
        record = session.get(RecordTable, task.t_record_id)
        commands = self._build_demo_commands(record.id if record else task.id)
        artifacts = self._materialise_capture_payload(task, commands)
        if record:
            record.r_progress_data = {"stage": "capture_completed", "timestamp": time.time()}
            record.r_camera_data = {
                "frames": 120,
                "exposure_ms": 12.5,
                "image_dir": artifacts.get("image_dir"),
                "images": artifacts.get("images"),
            }
            record.r_algorithm_data = {
                "commands": commands,
                "path_preview": self._build_demo_path(commands),
                "artifact_folder": artifacts.get("folder"),
                "image_dir": artifacts.get("image_dir"),
                "image_files": artifacts.get("images"),
            }
            record.r_warning_data = {"level": "info", "message": "Demo capture pipeline finished"}
        detail["phase"] = "completed"
        detail["finished_at"] = time.time()
        task.t_status = int(TaskStatus.COMPLETED)
        task.t_status_detail = detail
        self._update_status_table(session, run_status=1, machine_mode=2)
        LOG.info(
            "Capture task completed (task_id=%s record_id=%s artifacts=%s)",
            task.id,
            task.t_record_id,
            artifacts.get("folder"),
        )

        control_exists = session.execute(
            select(TaskTable)
            .where(TaskTable.t_task_type == int(TaskType.CONTROL))
            .where(TaskTable.t_record_id == task.t_record_id)
            .order_by(TaskTable.id.desc())
        ).scalar_one_or_none()
        if control_exists:
            return

        control_task = TaskTable(
            t_task_name=f"control-{task.t_record_id}",
            t_task_type=int(TaskType.CONTROL),
            t_workpiece_type=task.t_workpiece_type,
            t_material_type=task.t_material_type,
            t_status=int(TaskStatus.PENDING),
            t_workpiece_id=task.t_workpiece_id,
            t_record_id=task.t_record_id,
            t_payload={"commands": commands},
            t_status_detail={"phase": "queued"},
        )
        session.add(control_task)
        LOG.info(
            "Control task created (task_id=%s source_task=%s record_id=%s commands=%d)",
            control_task.id,
            task.id,
            task.t_record_id,
            len(commands),
        )

    def _complete_control_task(self, session: Session, task: TaskTable, detail: dict) -> None:
        detail["phase"] = "completed"
        detail["finished_at"] = time.time()
        task.t_status = int(TaskStatus.COMPLETED)
        task.t_status_detail = detail
        commands = (task.t_payload or {}).get("commands") or []
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
            task.t_record_id,
            len(commands),
        )

    def _complete_execute_task(self, session: Session, task: TaskTable, detail: dict) -> None:
        detail["phase"] = "completed"
        detail["finished_at"] = time.time()
        task.t_status = int(TaskStatus.COMPLETED)
        task.t_status_detail = detail
        self._update_status_table(session, run_status=1, machine_mode=1)
        self._mark_record_stage(session, task.t_record_id, "execute_completed")
        LOG.info(
            "Execute task completed (task_id=%s record_id=%s)",
            task.id,
            task.t_record_id,
        )

    # --------------------------------------------------------------- utilities

    def _materialise_capture_payload(self, task: TaskTable, commands: list[dict]) -> Dict[str, object]:
        folder = None
        payload = task.t_payload or {}
        raw_folder = payload.get("folder")
        if isinstance(raw_folder, str) and raw_folder:
            folder = Path(raw_folder)
        else:
            folder = self._save_dir / f"record_{task.t_record_id or task.id:06d}"
        folder.mkdir(parents=True, exist_ok=True)
        analysis_file = folder / "algorithm.json"
        with analysis_file.open("w", encoding="utf-8") as fp:
            json.dump({"commands": commands, "task_id": task.id}, fp, ensure_ascii=False, indent=2)
        image_dir = folder / "image"
        image_dir.mkdir(parents=True, exist_ok=True)
        images = self._copy_sample_images(image_dir)
        LOG.info(
            "Capture artifacts prepared at %s (images=%d)",
            folder,
            len(images),
        )
        return {
            "folder": str(folder),
            "algorithm_file": str(analysis_file),
            "image_dir": str(image_dir),
            "images": images,
        }

    def _build_demo_commands(self, seed: int) -> list[dict]:
        commands: list[dict] = []
        base = (seed or 1) % 7
        for idx in range(3):
            commands.append(
                {
                    "ex": round(5.0 + base * 2.0 + idx * 1.5, 3),
                    "ey": round(3.0 + base * 1.3 + idx * 0.9, 3),
                    "ez": round(-0.2 - idx * 0.05, 3),
                    "r": 1100 + idx * 120,
                    "v": 18.0 + idx * 3.5,
                }
            )
        return commands

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
            if owns_session:
                session.rollback()
        finally:
            if owns_session:
                session.close()

    def _build_demo_path(self, commands: list[dict]) -> list[dict]:
        points: list[dict] = []
        last_x = 0.0
        last_y = 0.0
        for index, cmd in enumerate(commands, start=1):
            x = float(cmd.get("ex", last_x))
            y = float(cmd.get("ey", last_y))
            points.append(
                {
                    "index": index,
                    "x": round(x, 3),
                    "y": round(y, 3),
                    "z": float(cmd.get("ez", 0.0)),
                    "velocity": float(cmd.get("v", 0.0)),
                }
            )
            last_x = x
            last_y = y
        return points


def _parse_cli_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the DemoTaskRunner against a database for local testing.")
    parser.add_argument(
        "--db-url",
        default="mysql+pymysql://root:nercar@127.0.0.1/MzPoliShineDB?charset=utf8mb4",
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
    engine = create_engine(args.db_url, future=True, pool_pre_ping=True, pool_recycle=1800)
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
