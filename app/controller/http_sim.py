from __future__ import annotations

import asyncio
import logging
import sys
from typing import Iterable, Optional

from app.controller.http_common import (
    DbStatusSource,
    SimulatedStatusSource,
    build_parser,
    run_controller,
)

SIM_DB_URL = "mysql+pymysql://mz:123456@192.168.2.32/MzPoliShineDB?charset=utf8mb4"
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

    if getattr(args, "disable_db", False):
        LOG.info("Simulated status mode selected; database polling disabled.")
    else:
        try:
            status_source = DbStatusSource(args.db_url)
            fallback_source = SimulatedStatusSource()
        except Exception as exc:
            LOG.warning("Failed to initialise DB status source (%s); falling back to simulated telemetry.", exc)
            status_source = SimulatedStatusSource()

    try:
        asyncio.run(run_controller(args, status_source=status_source, fallback_source=fallback_source))
    except KeyboardInterrupt:
        LOG.info("HTTP simulator interrupted by user.")


if __name__ == "__main__":
    main(sys.argv[1:])
