from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import and_, or_, select

from app import config as APP_CONFIG
from app.common import save_data
from app.common.tasks import TaskStatus, TaskType
from app.controller.demo_task_runner import DemoTaskRunner
from app.controller.http_common import (
    DbStatusSource,
    HttpBridgeFileLogger,
    SimulatedStatusSource,
    TaskQueueWriter,
    build_parser,
    run_controller,
)
from app.controller.http_common import program

try:
    from app.db.models.MzPoliShineDB import (
        HardwareTaskQueue,
        RecordTable,
        SystemLog,
    )  # type: ignore[import-error]
except Exception:  # pragma: no cover - optional dependency path
    HardwareTaskQueue = None  # type: ignore[assignment]
    RecordTable = None  # type: ignore[assignment]
    SystemLog = None  # type: ignore[assignment]

useLocTest = True
if useLocTest:
    PROD_DB_URL = "mysql+pymysql://remote_user:123456@127.0.0.1/MzPoliShineDB?charset=utf8mb4"
else:
    PROD_DB_URL = "mysql+pymysql://remote_user:123456@192.168.1.214/MzPoliShineDB?charset=utf8mb4"
LOG = logging.getLogger("controller.http_prod")
SAVE_DATA_DIR = APP_CONFIG.SAVE_DATA_ROOT
LOG_BASE_DIR = Path(APP_CONFIG.PROJECT_ROOT) / "logs" / "controller" / "httpbridge"


class TaskRunnerGroup:
    def __init__(self, runners: Iterable[object]) -> None:
        self._runners: List[object] = [runner for runner in runners if runner is not None]

    def tick(self) -> None:
        for runner in self._runners:
            try:
                runner.tick()
            except Exception as exc:  # pragma: no cover - defensive
                LOG.error("Task runner %s failed: %s", getattr(runner, "__class__", runner), exc)


class RecordArtifactRunner:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def tick(self) -> None:
        if RecordTable is None or HardwareTaskQueue is None:
            return
        with self._session_factory() as session:
            capture_tasks = (
                session.execute(
                    select(HardwareTaskQueue)
                    .where(HardwareTaskQueue.task_type == int(TaskType.CAPTURE))
                    .where(HardwareTaskQueue.status == int(TaskStatus.COMPLETED))
                    .order_by(HardwareTaskQueue.id.desc())
                    .limit(50)
                )
                .scalars()
                .all()
            )
            if not capture_tasks:
                return

            changed = False
            for task in capture_tasks:
                record_id = int(task.record_id or 0)
                if record_id <= 0:
                    continue
                record = session.get(RecordTable, record_id)
                if record is None:
                    continue

                camera_data = record.r_camera_data or {}
                if not isinstance(camera_data, dict):
                    camera_data = {}

                existing_images = camera_data.get("image_files") or []
                artifact_folder = camera_data.get("image_dir")
                pending = bool(camera_data.get("pending_copy"))

                if existing_images and artifact_folder and not pending:
                    continue

                folder = save_data.ensure_record_folder(int(record.id))
                save_data.copy_current_artifacts(folder)

                images_map: dict[str, str] = {}
                for item in folder.iterdir():
                    if item.is_file() and item.suffix.lower() in save_data.ALLOWED_ARTIFACT_EXTENSIONS:
                        images_map[item.name] = str(item)

                alg_path, alg_json = save_data.copy_alg_result(folder)
                program_payload: Optional[Dict[str, Any]] = None
                if alg_json:
                    try:
                        program_payload = program.build_program_payload_from_alg_data(alg_json)
                    except Exception as exc:  # pragma: no cover - defensive
                        LOG.warning("Unable to build program payload for record %s: %s", record.id, exc)
                camera_matrix = None
                if program_payload:
                    camera_matrix = program_payload.get("camera_to_robot_matrix")

                analysis_file = folder / "algorithm.json"
                try:
                    with analysis_file.open("w", encoding="utf-8") as fp:
                        json.dump(
                            {
                                "record_id": record.id,
                                "commands": program_payload.get("commands") if program_payload else [],
                                "copied_at": time.time(),
                            },
                            fp,
                            ensure_ascii=False,
                            indent=2,
                        )
                except Exception as exc:  # pragma: no cover - IO warnings
                    LOG.warning("Failed to write algorithm.json for record %s: %s", record.id, exc)

                try:
                    save_data.spawn_mesh_builder(int(record.id), folder)
                except Exception as exc:  # pragma: no cover - mesh conversion best effort
                    LOG.warning("Mesh generation skipped for record %s: %s", record.id, exc)

                updated_camera = dict(camera_data)
                updated_camera.update(
                    {
                        "pending_copy": False,
                        "image_dir": str(folder),
                        "images": images_map,
                        "image_files": sorted(images_map.keys()),
                    }
                )
                if alg_path:
                    updated_camera["alg_result_path"] = str(alg_path)
                if program_payload and program_payload.get("fixtures"):
                    updated_camera["fixtures"] = program_payload["fixtures"]
                if camera_matrix is not None:
                    updated_camera["camera_to_robot_matrix"] = camera_matrix
                    updated_camera["machine_matrix"] = camera_matrix

                record.r_camera_data = updated_camera
                try:
                    LOG.info(
                        "Record %s camera_to_robot_matrix=%s",
                        record.id,
                        json.dumps(updated_camera.get("camera_to_robot_matrix")),
                    )
                except Exception:
                    pass
                changed = True

            if changed:
                session.commit()


class SystemLogForwarder:
    LEVEL_MAP = {
        1: "DEBUG",
        2: "INFO",
        3: "SUCCESS",
        4: "WARNING",
        5: "ERROR",
    }
    SOURCE_MAP = {
        1: "system",
        2: "database",
        3: "device",
        4: "camera",
        5: "vision",
        6: "path",
        7: "command",
        8: "fixture",
    }

    def __init__(self, session_factory, *, batch_size: int = 100) -> None:
        self._session_factory = session_factory
        self._batch_size = max(int(batch_size), 1)
        now = datetime.utcnow()
        self._start_time = now
        self._cursor_time = now
        self._cursor_id = 0

    def poll(self) -> List[Dict[str, Any]]:
        if SystemLog is None:
            return []
        with self._session_factory() as session:
            stmt = (
                select(SystemLog)
                .where(
                    or_(
                        SystemLog.log_time > self._cursor_time,
                        and_(SystemLog.log_time == self._cursor_time, SystemLog.id > self._cursor_id),
                    )
                )
                .order_by(SystemLog.log_time.asc(), SystemLog.id.asc())
                .limit(self._batch_size)
            )
            rows = session.execute(stmt).scalars().all()
        if not rows:
            return []

        entries: List[Dict[str, Any]] = []
        for row in rows:
            entries.append(self._serialize(row))

        last = rows[-1]
        if last.log_time:
            self._cursor_time = last.log_time
        self._cursor_id = int(getattr(last, "id", self._cursor_id) or self._cursor_id)
        return entries

    @property
    def start_time(self) -> datetime:
        return self._start_time

    def _serialize(self, row: SystemLog) -> Dict[str, Any]:
        log_ts = self._to_timestamp(getattr(row, "log_time", None))
        level_name = self.LEVEL_MAP.get(int(getattr(row, "log_type", 0) or 0), "INFO")
        source_label = self.SOURCE_MAP.get(int(getattr(row, "info_type", 0) or 0), "system")
        message = str(getattr(row, "content", ""))
        return {
            "ts": log_ts,
            "level": level_name,
            "name": source_label,
            "msg": message,
            "log_type": getattr(row, "log_type", None),
            "info_type": getattr(row, "info_type", None),
        }

    @staticmethod
    def _to_timestamp(value: Optional[datetime]) -> float:
        if value is None:
            return time.time()
        try:
            return value.timestamp()
        except Exception:
            return time.time()


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser(
        "HTTP production controller that streams StatusTable snapshots.",
        default_label="http-prod",
        default_db_url=PROD_DB_URL,
    )
    parser.add_argument(
        "--spawn-demo-runner",
        action="store_true",
        help="同时启动内置 DemoTaskRunner（默认关闭，需要单独运行 demo_task_runner）。",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        logging.getLogger().setLevel(logging.INFO)

    task_runner = None
    file_logger = HttpBridgeFileLogger(LOG_BASE_DIR)

    try:
        import app.db as app_db  # pylint: disable=import-error
    except Exception as exc:
        LOG.warning("Database module unavailable; skipping init: %s", exc)
        app_db = None  # type: ignore[assignment]
    else:
        try:
            app_db.init_db()
            from app.db.seed import seed_tool_data, seed_workpiece_data, seed_cutting_status_data

            seed_tool_data(app_db.SessionLocal)
            seed_workpiece_data(app_db.SessionLocal)
            seed_cutting_status_data(app_db.SessionLocal)
        except Exception as exc:
            LOG.warning("Database initialisation failed: %s", exc, exc_info=False)

    log_forwarder = None
    try:
        status_source = DbStatusSource(args.db_url)
        fallback_source = SimulatedStatusSource()
        task_writer = TaskQueueWriter(status_source.session_factory, engine=status_source.engine)
        artifact_runner = RecordArtifactRunner(status_source.session_factory)
        runners: List[object] = [artifact_runner]
        if getattr(args, "spawn_demo_runner", False):
            demo_runner = DemoTaskRunner(
                status_source.session_factory,
                save_dir=SAVE_DATA_DIR,
                task_writer=task_writer,
            )
            LOG.info("Inline DemoTaskRunner enabled (--spawn-demo-runner).")
            runners.insert(0, demo_runner)
        else:
            LOG.info("DemoTaskRunner disabled; running artifact copy tasks only.")
        task_runner = TaskRunnerGroup(runners)
        if SystemLog is None:
            LOG.warning("SystemLog model unavailable; third-party log forwarding disabled.")
        else:
            log_forwarder = SystemLogForwarder(status_source.session_factory)
            LOG.info(
                "SystemLog forwarder initialised and watching for new entries after %s.",
                log_forwarder.start_time.isoformat(),
            )
    except Exception as exc:
        LOG.error("Unable to initialise production database source: %s", exc)
        raise SystemExit(1) from exc

    try:
        asyncio.run(
            run_controller(
                args,
                status_source=status_source,
                fallback_source=fallback_source,
                task_writer=task_writer,
                task_runner=task_runner,
                file_logger=file_logger,
                log_forwarder=log_forwarder,
            )
        )
    except KeyboardInterrupt:
        LOG.info("HTTP production controller interrupted by user.")


if __name__ == "__main__":
    main(sys.argv[1:])
