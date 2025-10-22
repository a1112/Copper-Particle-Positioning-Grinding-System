from __future__ import annotations

try:
    from gevent import monkey as _gevent_monkey
except ImportError:  # pragma: no cover - zerorpc installs gevent in normal deployments
    _gevent_monkey = None
else:  # pragma: no cover - side effect only
    _gevent_monkey.patch_all()

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional, Mapping

from app.config import RPC_CONTROL_ENDPOINT, RPC_LISTEN_ENDPOINT, RPC_TIMEOUT
from app.controller.rpc.service import RpcControllerService

LOG = logging.getLogger("controller")


@dataclass
class Scenario:
    """Container describing one control snapshot to push to the server."""

    name: str
    status: Dict[str, Any]
    cutting: Optional[Dict[str, Any]] = None
    delay: float = 1.0
    logs: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "Scenario":
        name = str(payload.get("label") or payload.get("name") or "unnamed")
        status_payload = payload.get("status") or {}
        cutting_payload = payload.get("cutting")
        logs_payload = payload.get("logs")
        delay_value = payload.get("delay", 1.0)
        try:
            delay = float(delay_value)
        except Exception:
            delay = 1.0
        if delay < 0:
            delay = 0.0

        logs: Optional[List[Dict[str, Any]]] = None
        if isinstance(logs_payload, Iterable):
            parsed: List[Dict[str, Any]] = []
            for entry in logs_payload:
                if isinstance(entry, Mapping):
                    parsed.append(dict(entry))
            if parsed:
                logs = parsed

        return cls(
            name=name,
            status=dict(status_payload),
            cutting=dict(cutting_payload) if isinstance(cutting_payload, Mapping) else None,
            delay=delay,
            logs=logs,
        )


def _apply_scenario_rpc(service: RpcControllerService, scenario: Scenario) -> None:
    status_payload = dict(scenario.status)
    status_payload.setdefault("label", scenario.name)
    ok_status = service.publish_status(status_payload)
    LOG.info("Published status snapshot %s via RPC (ok=%s)", scenario.name, ok_status)

    if scenario.cutting:
        ok_cutting = service.publish_cutting(scenario.cutting)
        LOG.info("Published cutting snapshot %s via RPC (ok=%s)", scenario.name, ok_cutting)
    if scenario.logs:
        ok_logs = service.publish_logs(scenario.logs)
        LOG.info("Published %d log entries via RPC (ok=%s)", len(scenario.logs), ok_logs)


def _load_scenarios(paths: Iterable[Path]) -> List[Scenario]:
    scenarios: List[Scenario] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            items = payload
        else:
            items = payload.get("scenarios") if isinstance(payload, dict) else None
            if not isinstance(items, list):
                raise ValueError(f"Unsupported scenario file format: {path}")
        for item in items:
            if isinstance(item, dict):
                scenarios.append(Scenario.from_mapping(item))
    if not scenarios:
        raise ValueError("No scenarios were loaded")
    return scenarios


async def _cycle_scenarios(scenarios: List[Scenario], loop: bool) -> AsyncIterator[Scenario]:
    while True:
        for scenario in scenarios:
            yield scenario
        if not loop:
            break


async def run_controller(args: argparse.Namespace) -> None:
    paths = [Path(item) for item in args.scenario]
    scenarios = _load_scenarios(paths)

    service = RpcControllerService(
        listen_endpoint=args.rpc_listen,
        server_endpoint=args.rpc_server,
        timeout=args.rpc_timeout,
    )
    service.start()
    LOG.info(
        "RPC controller started (listen=%s, upstream=%s)",
        args.rpc_listen,
        args.rpc_server,
    )

    try:
        if not service.ping():
            LOG.warning("Initial RPC ping failed; continuing regardless")
        async for scenario in _cycle_scenarios(scenarios, args.loop):
            _apply_scenario_rpc(service, scenario)
            await asyncio.sleep(scenario.delay if args.respect_delay else args.interval)
    finally:
        service.stop()
        LOG.info("RPC controller stopped")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone main-controller that drives the server simulator payloads over ZeroRPC.")
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
        "--rpc-listen",
        default=RPC_CONTROL_ENDPOINT,
        help=f"ZeroRPC endpoint where the controller listens for commands (default: {RPC_CONTROL_ENDPOINT}).",
    )
    parser.add_argument(
        "--rpc-server",
        default=RPC_LISTEN_ENDPOINT,
        help=f"ZeroRPC endpoint exposed by the API server to receive telemetry (default: {RPC_LISTEN_ENDPOINT}).",
    )
    parser.add_argument(
        "--rpc-timeout",
        type=float,
        default=RPC_TIMEOUT,
        help=f"Timeout (seconds) for ZeroRPC requests (default: {RPC_TIMEOUT}).",
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
