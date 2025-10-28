from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Iterable, Optional

from app import config as APP_CONFIG
from app.controller.demo_task_runner import DemoTaskRunner
from app.controller.http_common import (
    DbStatusSource,
    HttpBridgeFileLogger,
    SimulatedStatusSource,
    TaskQueueWriter,
    build_parser,
    run_controller,
)

useLocTest = True
if useLocTest:
    PROD_DB_URL = "mysql+pymysql://root:nercar@127.0.0.1/MzPoliShineDB?charset=utf8mb4"
else:
    PROD_DB_URL = "mysql+pymysql://remote_user:123456@192.168.1.214/MzPoliShineDB?charset=utf8mb4"
LOG = logging.getLogger("controller.http_prod")
SAVE_DATA_DIR = Path(APP_CONFIG.PROJECT_ROOT) / "SaveData"
LOG_BASE_DIR = Path(APP_CONFIG.PROJECT_ROOT) / "logs" / "controller" / "httpbridge"


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
        status_source = DbStatusSource(args.db_url)
        fallback_source = SimulatedStatusSource()
        task_writer = TaskQueueWriter(status_source.session_factory, engine=status_source.engine)
        if getattr(args, "spawn_demo_runner", False):
            task_runner = DemoTaskRunner(
                status_source.session_factory,
                save_dir=SAVE_DATA_DIR,
                task_writer=task_writer,
            )
            LOG.info("Inline DemoTaskRunner 已启用 (--spawn-demo-runner)。")
        else:
            LOG.info("未启用内置 DemoTaskRunner，请单独运行 `python -m app.controller.demo_task_runner`。")
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
