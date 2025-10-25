from __future__ import annotations

import asyncio
import logging
import sys
from typing import Iterable, Optional

from app.controller.http_common import (
    DbStatusSource,
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


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser(
        "HTTP production controller that streams StatusTable snapshots.",
        default_label="http-prod",
        default_db_url=PROD_DB_URL,
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        logging.getLogger().setLevel(logging.INFO)

    try:
        status_source = DbStatusSource(args.db_url)
        fallback_source = SimulatedStatusSource()
        task_writer = TaskQueueWriter(status_source.session_factory, engine=status_source.engine)
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
            )
        )
    except KeyboardInterrupt:
        LOG.info("HTTP production controller interrupted by user.")


if __name__ == "__main__":
    main(sys.argv[1:])
