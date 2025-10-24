from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Iterable, Optional

from app.config import (
    HTTP_BRIDGE_BASE,
    HTTP_CONTROL_ENDPOINT,
    HTTP_TIMEOUT,
    RPC_CONTROL_ENDPOINT,
    RPC_LISTEN_ENDPOINT,
    RPC_TIMEOUT,
)
from app.controller.business import run_controller

LOG = logging.getLogger("controller.cli")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone main-controller that drives the server simulator payloads over gRPC or HTTP.")
    parser.add_argument(
        "-s",
        "--scenario",
        action="append",
        default=[],
        help="Path to a JSON file describing scenarios (may be provided multiple times).",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=2.0,
        help="Fallback delay between scenarios when --respect-delay is disabled.",
    )
    parser.add_argument(
        "--respect-delay",
        action="store_true",
        help="Use the `delay` value inside each scenario (if present).",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Keep replaying scenarios in a loop until interrupted.",
    )
    parser.add_argument(
        "--transport",
        choices=["grpc", "http"],
        default="http",
        help="Transport used to push data to the API server (default: grpc).",
    )
    parser.add_argument(
        "--rpc-listen",
        default=RPC_CONTROL_ENDPOINT,
        help=f"gRPC endpoint where the controller listens for commands (default: {RPC_CONTROL_ENDPOINT}).",
    )
    parser.add_argument(
        "--rpc-server",
        default=RPC_LISTEN_ENDPOINT,
        help=f"gRPC endpoint exposed by the API server to receive telemetry (default: {RPC_LISTEN_ENDPOINT}).",
    )
    parser.add_argument(
        "--rpc-timeout",
        type=float,
        default=RPC_TIMEOUT,
        help=f"Timeout (seconds) for gRPC requests (default: {RPC_TIMEOUT}).",
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
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.scenario:
        default_path = Path(__file__).resolve().parent.joinpath("sample_scenarios.json")
        args.scenario = [str(default_path)]

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(message)s")

    try:
        asyncio.run(run_controller(args))
    except KeyboardInterrupt:
        LOG.info("Controller interrupted by user.")
    except Exception as exc:  # pragma: no cover - top-level safeguard
        LOG.exception("Controller crashed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
