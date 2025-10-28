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

SIM_DB_URL = "mysql+pymysql://root:nercar@127.0.0.1/MzPoliShineDB?charset=utf8mb4"
LOG = logging.getLogger("controller.http_sim")


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser(
        "HTTP simulator that replays synthetic telemetry (optional StatusTable polling).",
        default_label="http-sim",
        default_db_url=SIM_DB_URL,
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        logging.getLogger().setLevel(logging.INFO)

    status_source = SimulatedStatusSource()
    fallback_source = None

    task_writer = None

    if getattr(args, "disable_db", False):
        LOG.info("Simulated status mode selected; database polling disabled.")
    else:
        try:
            status_source = DbStatusSource(args.db_url)
            fallback_source = SimulatedStatusSource()
            task_writer = TaskQueueWriter(status_source.session_factory, engine=status_source.engine)
        except Exception as exc:
            LOG.warning("Failed to initialise DB status source (%s); falling back to simulated telemetry.", exc)
            status_source = SimulatedStatusSource()
            try:
                task_writer = TaskQueueWriter.from_url(args.db_url)
            except Exception as writer_exc:
                LOG.warning("Failed to initialise task queue writer (%s); command logging disabled.", writer_exc)

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
        LOG.info("HTTP simulator interrupted by user.")


if __name__ == "__main__":
    main(sys.argv[1:])
