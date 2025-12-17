from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from app.config import HTTP_BRIDGE_BASE, HTTP_CONTROL_ENDPOINT, HTTP_TIMEOUT
from app.controller.httpbridge import HttpControllerService

from .control import create_control_handler
from .logger import HttpBridgeFileLogger
from .state import ControllerState
from .status import DbStatusSource, SimulatedStatusSource, StatusSourceProtocol, read_cutting_payload
from .tasks import TaskQueueWriter

LOG = logging.getLogger("controller.http.runner")


def build_parser(
    description: str,
    *,
    default_label: str,
    default_db_url: Optional[str] = None,
    default_device_id: str = "GRINDER-01",
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--label", default=default_label, help=f"Label field in status payloads (default: {default_label}).")
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
    if default_db_url is not None:
        parser.add_argument(
            "--db-url",
            default=default_db_url,
            help=f"Database URL for StatusTable polling (default: {default_db_url}).",
        )
        parser.add_argument(
            "--disable-db",
            action="store_true",
            help="Ignore the configured database and emit purely simulated status data.",
        )
    parser.add_argument(
        "--device-id",
        default=default_device_id,
        help=f"Device identifier recorded in hardware task queue (default: {default_device_id}).",
    )
    return parser


def _parse_control_endpoint(url: str) -> Tuple[str, int]:
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 9001
    return host, port


def _flush_command_logs(
    service: HttpControllerService,
    state: ControllerState,
    file_logger: Optional[HttpBridgeFileLogger] = None,
) -> int:
    if not state.command_log:
        return 0
    entries: List[Dict[str, object]] = list(state.command_log)
    state.command_log.clear()
    ok = False
    try:
        ok = service.publish_logs(entries)
    finally:
        if file_logger:
            file_logger.write_many(
                "control",
                ({**entry, "published": bool(ok)} for entry in entries),
            )
    return len(entries)


async def run_controller(
    args: argparse.Namespace,
    *,
    status_source: StatusSourceProtocol,
    fallback_source: Optional[StatusSourceProtocol] = None,
    task_writer: Optional[TaskQueueWriter] = None,
    task_runner: Optional[object] = None,
    file_logger: Optional[HttpBridgeFileLogger] = None,
    log_forwarder: Optional[object] = None,
) -> None:
    state = ControllerState(label=args.label)
    control_host, control_port = _parse_control_endpoint(args.http_control)
    LOG.info(
        "Controller starting (label=%s interval=%.2fs log_every=%d base=%s control=%s)",
        args.label,
        args.interval,
        args.log_every,
        args.http_base,
        args.http_control,
    )
    if getattr(args, "probe_bridge", False):
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
    service.register_control_handler(create_control_handler(state, task_writer, device_id=args.device_id))
    service.start()
    LOG.info("Control listener ready at http://%s:%s/control", control_host, control_port)

    session_factory = getattr(status_source, "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Status source does not expose session_factory; cutting telemetry requires database access.")

    stop_event = asyncio.Event()

    def _signal_handler(*_: Any) -> None:
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
            cycle = tick * args.interval
            try:
                status_payload = status_source.build(state, timestamp, cycle)
            except Exception:
                if fallback_source is None:
                    LOG.exception("Status build failed and fallback is disabled.")
                    raise
                LOG.exception("Status build failed; using fallback source.")
                status_payload = fallback_source.build(state, timestamp, cycle)
            try:
                cutting_payload = read_cutting_payload(session_factory)
            except Exception as exc:
                LOG.exception("Cutting payload build failed.")
                raise

            try:
                ok_status = service.publish_status(status_payload)
                LOG.info(
                    "Status push ok=%s rpm=%.2f",
                    ok_status,
                    status_payload.get("spindle_rpm", 0.0),
                )
                if file_logger:
                    file_logger.write("status", status_payload, ok=bool(ok_status))
            except Exception as exc:
                LOG.error("Status push failed: %s", exc)
                if file_logger:
                    file_logger.write("status", status_payload, ok=False, error=str(exc))
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
                if file_logger:
                    file_logger.write("cutting", cutting_payload, ok=bool(ok_cutting))
            except Exception as exc:
                LOG.error("Cutting push failed: %s", exc)
                if file_logger:
                    file_logger.write("cutting", cutting_payload, ok=False, error=str(exc))
                await asyncio.sleep(args.interval)
                continue

            if state.program_running:
                state.advance_program()
            program_snapshot = state.program_snapshot()
            if program_snapshot is not None:
                try:
                    ok_program = service.publish_program(program_snapshot)
                    LOG.info("Program push ok=%s current=%s", ok_program, program_snapshot["program_state"].get("current"))
                    if file_logger:
                        file_logger.write("program", program_snapshot, ok=bool(ok_program))
                except Exception as exc:
                    LOG.error("Program push failed: %s", exc)
                    if file_logger:
                        file_logger.write("program", program_snapshot, ok=False, error=str(exc))

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
                    if file_logger:
                        file_logger.write("logs", log_entry, ok=bool(ok_log))
                except Exception as exc:
                    LOG.error("Heartbeat log push failed: %s", exc)
                    if file_logger:
                        file_logger.write("logs", log_entry, ok=False, error=str(exc))

            try:
                flushed = _flush_command_logs(service, state, file_logger=file_logger)
                if flushed:
                    LOG.info("Flushed %d control log entries", flushed)
            except Exception as exc:
                LOG.error("Control log flush failed: %s", exc)

            if log_forwarder is not None:
                try:
                    db_logs = await asyncio.to_thread(log_forwarder.poll)
                    # cursor_id = getattr(log_forwarder, "cursor_id", None)
                    # if cursor_id is not None:
                    #     LOG.info("System log poll completed entries=%d cursor=%s", len(db_logs), cursor_id)
                    # else:
                    #     LOG.info("System log poll completed entries=%d", len(db_logs))
                except Exception as exc:
                    LOG.error("System log poll failed: %s", exc)
                    db_logs = []
                if db_logs:
                    try:
                        ok_third = service.publish_logs(db_logs)
                        if file_logger:
                            file_logger.write_many("third_party_logs", db_logs, ok=bool(ok_third))
                    except Exception as exc:
                        LOG.error("System log push failed: %s", exc)
                        if file_logger:
                            file_logger.write_many("third_party_logs", db_logs, ok=False, error=str(exc))

            if task_runner is not None:
                try:
                    await asyncio.to_thread(task_runner.tick)
                except Exception as exc:
                    LOG.error("Task runner tick failed: %s", exc)

            tick += 1
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=args.interval)
            except asyncio.TimeoutError:
                continue
    finally:
        service.stop()
        close_builder = getattr(status_source, "close", None)
        if callable(close_builder):
            try:
                close_builder()
            except Exception:
                pass
        if task_writer is not None:
            task_writer.close()


__all__ = [
    "build_parser",
    "run_controller",
    "DbStatusSource",
    "SimulatedStatusSource",
    "TaskQueueWriter",
    "HttpBridgeFileLogger",
]
