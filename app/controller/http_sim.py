from __future__ import annotations

import argparse
import asyncio
import logging
import math
import signal
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse

import requests

from app.config import HTTP_BRIDGE_BASE, HTTP_CONTROL_ENDPOINT, HTTP_TIMEOUT
from app.controller.httpbridge import HttpControllerService

LOG = logging.getLogger("controller.http_sim")


@dataclass
class ControllerState:
    """Mutable state used to synthesise telemetry snapshots."""

    label: str = "http-sim"
    run_mode: str = "HTTP"
    spindle_rpm: float = 1200.0
    torque_bias: float = 0.3
    command_log: List[Dict[str, str]] = field(default_factory=list)

    def register_command(self, action: str, ok: bool, message: str) -> None:
        self.command_log.append(
            {
                "ts": time.time(),
                "level": "INFO" if ok else "WARN",
                "name": "controller",
                "msg": f"control action={action} message={message}",
            }
        )


def _control_handler(state: ControllerState):
    def handler(action: str, params: Dict[str, object]) -> Dict[str, object]:
        normalized = action.strip().lower()
        if not normalized:
            state.register_command(action, False, "Empty action")
            return {"ok": False, "message": "Empty action"}

        if normalized == "reset":
            state.spindle_rpm = 1100.0
            state.torque_bias = 0.2
            state.register_command(action, True, "Reset acknowledged")
            return {"ok": True, "message": "Reset acknowledged"}

        if normalized == "boost":
            state.spindle_rpm += 50.0
            state.torque_bias = min(state.torque_bias + 0.05, 0.6)
            state.register_command(action, True, "Boost applied")
            return {"ok": True, "message": "Boost applied"}

        state.register_command(action, False, f"Unsupported action: {action}")
        return {"ok": False, "message": f"Unsupported action: {action}"}

    return handler


def _build_status_payload(state: ControllerState, timestamp: float, cycle: float) -> Dict[str, object]:
    spindle = state.spindle_rpm + 40.0 * math.sin(cycle * 0.3)
    torque = state.torque_bias + 0.1 * abs(math.sin(cycle * 0.5))
    x = 120.0 + 2.0 * math.sin(cycle * 0.2)
    y = 60.0 + 1.5 * math.sin(cycle * 0.17)
    z = -0.4 + 0.05 * math.cos(cycle * 0.11)
    theta = math.degrees(math.sin(cycle * 0.07)) * 0.5

    return {
        "label": state.label,
        "ts": timestamp,
        "state": "RUNNING",
        "run_mode": state.run_mode,
        "serial_number": f"HTTP-{int(timestamp)}",
        "spindle_rpm": round(spindle, 2),
        "spindle_torque": round(torque, 3),
        "position": {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "theta": round(theta, 3)},
        "statusLights": {
            "controller": "READY",
            "server": True,
            "spindle": "RUNNING" if spindle > 1100 else "READY",
            "motion": "RUNNING",
        },
    }


def _build_cutting_payload(state: ControllerState, timestamp: float, cycle: float) -> Dict[str, object]:
    feed = 20.0 + 4.0 * math.sin(cycle * 0.33)
    downfeed_target = 0.75
    downfeed_current = downfeed_target * (0.5 + 0.5 * (1 + math.sin(cycle * 0.1)) / 2)
    removal_expected = 120.0
    removal_current = removal_expected * (0.3 + 0.2 * (1 + math.sin(cycle * 0.08)))
    torque = state.torque_bias + 0.12 * abs(math.sin(cycle * 0.55))

    return {
        "ts": timestamp,
        "feed_rate": round(feed, 3),
        "downfeed_target": round(downfeed_target, 3),
        "downfeed_current": round(downfeed_current, 3),
        "removal_current": round(removal_current, 3),
        "removal_expected": round(removal_expected, 3),
        "torque_max": round(max(torque, state.torque_bias + 0.15), 3),
        "torque": round(torque, 3),
        "elapsed_sec": round(cycle, 2),
    }


def _flush_command_logs(service: HttpControllerService, state: ControllerState) -> int:
    if not state.command_log:
        return 0
    entries: List[Dict[str, object]] = list(state.command_log)
    state.command_log.clear()
    service.publish_logs(entries)
    return len(entries)


def _parse_control_endpoint(url: str) -> tuple[str, int]:
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 9001
    return host, port


async def run_simulator(args: argparse.Namespace) -> None:
    state = ControllerState(label=args.label)
    control_host, control_port = _parse_control_endpoint(args.http_control)
    LOG.info(
        "HTTP simulator starting (label=%s interval=%.2fs log_every=%d base=%s control=%s)",
        args.label,
        args.interval,
        args.log_every,
        args.http_base,
        args.http_control,
    )
    if args.probe_bridge:
        try:
            resp = requests.get(f"{args.http_base.rstrip('/')}/ping", timeout=args.http_timeout)
            resp.raise_for_status()
        except requests.RequestException as exc:
            LOG.error("Bridge ping failed (%s): %s", args.http_base, exc)
        else:
            LOG.info("Bridge ping ok (%s)", args.http_base)
    service = HttpControllerService(
        base_url=args.http_base,
        control_host=control_host,
        control_port=control_port,
        timeout=args.http_timeout,
    )
    service.register_control_handler(_control_handler(state))
    service.start()
    LOG.info("Control listener ready at http://%s:%s/control", control_host, control_port)

    stop_event = asyncio.Event()

    def _signal_handler(*_):
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _signal_handler)
        except Exception:
            pass

    tick = 0
    try:
        while not stop_event.is_set():
            timestamp = time.time()
            status_payload = _build_status_payload(state, timestamp, tick * args.interval)
            cutting_payload = _build_cutting_payload(state, timestamp, tick * args.interval)

            try:
                ok_status = service.publish_status(status_payload)
                LOG.info(
                    "Status push ok=%s rpm=%.2f torque=%.3f",
                    ok_status,
                    status_payload.get("spindle_rpm", 0.0),
                    status_payload.get("spindle_torque", 0.0),
                )
            except Exception as exc:
                LOG.error("Status push failed: %s", exc)
                await asyncio.sleep(args.interval)
                continue

            try:
                ok_cutting = service.publish_cutting(cutting_payload)
                LOG.info(
                    "Cutting push ok=%s feed=%.2f torque=%.3f elapsed=%.2f",
                    ok_cutting,
                    cutting_payload.get("feed_rate", 0.0),
                    cutting_payload.get("torque", 0.0),
                    cutting_payload.get("elapsed_sec", 0.0),
                )
            except Exception as exc:
                LOG.error("Cutting push failed: %s", exc)
                await asyncio.sleep(args.interval)
                continue

            if tick % args.log_every == 0:
                log_entry = {
                    "ts": timestamp,
                    "level": "INFO",
                    "name": "controller.sim",
                    "msg": f"heartbeat cycle={tick}",
                }
                try:
                    ok_log = service.publish_logs([log_entry])
                    LOG.info("Heartbeat log push ok=%s cycle=%d", ok_log, tick)
                except Exception as exc:
                    LOG.error("Heartbeat log push failed: %s", exc)

            try:
                flushed = _flush_command_logs(service, state)
                if flushed:
                    LOG.info("Flushed %d control log entries", flushed)
            except Exception as exc:
                LOG.error("Control log flush failed: %s", exc)

            tick += 1
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=args.interval)
            except asyncio.TimeoutError:
                continue
    finally:
        service.stop()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HTTP controller simulator that streams synthetic telemetry.")
    parser.add_argument("--label", default="http-sim", help="Label field in status payloads (default: http-sim).")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Interval between telemetry pushes in seconds (default: 1.0).",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=5,
        help="Publish a heartbeat log every N intervals (default: 5).",
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
        "--probe-bridge",
        action="store_true",
        help="Perform an initial GET /bridge/ping check before streaming telemetry.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        logging.getLogger().setLevel(logging.INFO)

    try:
        asyncio.run(run_simulator(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
