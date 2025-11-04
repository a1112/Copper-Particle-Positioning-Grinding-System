from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional

from sqlalchemy import select

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

try:
    from app.db.models.MzPoliShineDB import HardwareTaskQueue, RecordTable  # type: ignore[import-error]
except Exception:  # pragma: no cover - optional dependency path
    HardwareTaskQueue = None  # type: ignore[assignment]
    RecordTable = None  # type: ignore[assignment]

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
                session.rollback()
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
                algo_data = record.r_algorithm_data or {}
                if not isinstance(camera_data, dict):
                    camera_data = {}
                if not isinstance(algo_data, dict):
                    algo_data = {}

                existing_images = camera_data.get("image_files") or algo_data.get("image_files") or []
                artifact_folder = algo_data.get("artifact_folder")
                pending = bool(camera_data.get("pending_copy") or algo_data.get("pending_copy"))

                if existing_images and artifact_folder and not pending:
                    continue

                folder = save_data.ensure_record_folder(int(record.id))
                save_data.copy_current_artifacts(folder)

                images_map: dict[str, str] = {}
                for item in folder.iterdir():
                    if item.is_file() and item.suffix.lower() in save_data.ALLOWED_ARTIFACT_EXTENSIONS:
                        images_map[item.name] = str(item)

                alg_path, alg_json = save_data.copy_alg_result(folder)
                camera_matrix = None
                if alg_json:
                    camera_matrix = DemoTaskRunner._normalise_camera_matrix(
                        alg_json.get("cameraToRobotHomMat3d")
                    )

                analysis_file = folder / "algorithm.json"
                try:
                    with analysis_file.open("w", encoding="utf-8") as fp:
                        json.dump(
                            {
                                "record_id": record.id,
                                "commands": algo_data.get("commands"),
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

                updated_algo = dict(algo_data)
                updated_algo.update(
                    {
                        "pending_copy": False,
                        "artifact_folder": str(folder),
                        "algorithm_file": str(analysis_file),
                        "image_dir": str(folder),
                        "image_files": sorted(images_map.keys()),
                    }
                )
                if alg_path:
                    updated_algo["alg_result_path"] = str(alg_path)
                if alg_json is not None:
                    updated_algo["alg_result"] = alg_json
                if camera_matrix is not None:
                    updated_algo["camera_to_robot_matrix"] = camera_matrix
                    updated_algo["machine_matrix"] = camera_matrix
                updated_algo.setdefault("commands", algo_data.get("commands", []))

                record.r_camera_data = updated_camera
                record.r_algorithm_data = updated_algo
                try:
                    LOG.info(
                        "Record %s camera_to_robot_matrix=%s",
                        record.id,
                        json.dumps(updated_algo.get("camera_to_robot_matrix")),
                    )
                except Exception:
                    pass
                changed = True

            if changed:
                session.commit()
            else:
                session.rollback()


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
            )
        )
    except KeyboardInterrupt:
        LOG.info("HTTP production controller interrupted by user.")


if __name__ == "__main__":
    main(sys.argv[1:])
