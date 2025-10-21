from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional

import httpx

DEFAULT_API_BASE = "http://127.0.0.1:8010/api"

LOG = logging.getLogger("controller")


@dataclass
class Scenario:
    """Container describing one control snapshot to push to the server."""

    name: str
    status: Dict[str, Any]
    cutting: Optional[Dict[str, Any]] = None
    delay: float = 1.0

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "Scenario":
        name = str(payload.get("label") or payload.get("name") or "unnamed")
        status_payload = payload.get("status") or {}
        cutting_payload = payload.get("cutting")
        delay_value = payload.get("delay", 1.0)
        try:
            delay = float(delay_value)
        except Exception:
            delay = 1.0
        if delay < 0:
            delay = 0.0
        return cls(name=name, status=dict(status_payload), cutting=dict(cutting_payload) if cutting_payload else None, delay=delay)


async def _request_json(
    client: httpx.AsyncClient,
    base: str,
    endpoint: str,
    *,
    method: str = "POST",
    payload: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = f"{base.rstrip('/')}/{endpoint.lstrip('/')}"
    LOG.debug("%s %s", method.upper(), url)
    if method == "POST":
        response = await client.post(url, params=params, json=payload)
    elif method == "DELETE":
        response = await client.delete(url, params=params)
    else:
        response = await client.request(method, url, params=params, json=payload)
    response.raise_for_status()
    if not response.content:
        return {}
    return response.json()


async def _apply_scenario(
    client: httpx.AsyncClient,
    base: str,
    scenario: Scenario,
    merge: bool,
) -> None:
    status_payload = dict(scenario.status)
    status_payload.setdefault("label", scenario.name)
    await _request_json(client, base, "status/test_payload", params={"merge": "true" if merge else "false"}, payload=status_payload)
    LOG.info("Applied status snapshot %s", scenario.name)
    if scenario.cutting:
        await _request_json(client, base, "cutting/test_payload", params={"merge": "true" if merge else "false"}, payload=scenario.cutting)
        LOG.info("Applied cutting snapshot %s", scenario.name)


async def _clear_manual_payloads(client: httpx.AsyncClient, base: str) -> None:
    try:
        LOG.info("Clearing manual status overrides")
        await _request_json(client, base, "status/test_payload", method="DELETE")
    except httpx.HTTPStatusError:
        pass
    try:
        LOG.info("Clearing manual cutting overrides")
        await _request_json(client, base, "cutting/test_payload", method="DELETE")
    except httpx.HTTPStatusError:
        pass


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
            if not isinstance(item, dict):
                continue
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

    timeout = httpx.Timeout(args.timeout, connect=args.timeout)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            async for scenario in _cycle_scenarios(scenarios, args.loop):
                await _apply_scenario(client, args.base, scenario, merge=args.merge)
                await asyncio.sleep(scenario.delay if args.respect_delay else args.interval)
        finally:
            if args.reset_on_exit:
                await _clear_manual_payloads(client, args.base)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone main-controller that drives the server simulator payloads.")
    parser.add_argument(
        "-b",
        "--base",
        default=DEFAULT_API_BASE,
        help=f"Server API base URL (default: {DEFAULT_API_BASE})",
    )
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
        "--merge",
        action="store_true",
        help="Merge scenarios into existing overrides instead of overwriting on each push.",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Keep replaying scenarios in a loop until interrupted.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout (seconds) for HTTP requests.",
    )
    parser.add_argument(
        "--reset-on-exit",
        action="store_true",
        help="Clear manual payload overrides when the controller stops.",
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
    except httpx.HTTPError as exc:
        LOG.error("HTTP error: %s", exc)
        raise SystemExit(2) from exc
    except Exception as exc:  # pragma: no cover - top-level safeguard
        LOG.exception("Controller crashed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
