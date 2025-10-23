from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Any, Dict

from app.config import RPC_LISTEN_ENDPOINT, RPC_TIMEOUT
from app.controller.rpc.client import ControllerRpcClient

LOG = logging.getLogger("controller.rpc.test")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal gRPC connectivity test between controller and API.")
    parser.add_argument(
        "--endpoint",
        default=RPC_LISTEN_ENDPOINT,
        help=f"gRPC endpoint exposed by the API server (default: {RPC_LISTEN_ENDPOINT}).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=RPC_TIMEOUT,
        help=f"RPC call timeout in seconds (default: {RPC_TIMEOUT}).",
    )
    parser.add_argument(
        "--label",
        default="rpc_test",
        help="Label to attach to the status payload (default: rpc_test).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only ping the RPC endpoint without pushing payloads.",
    )
    return parser


def _status_payload(label: str) -> Dict[str, Any]:
    now = int(time.time())
    return {
        "label": label,
        "state": "TESTING",
        "serial_number": f"TEST-{now}",
        "run_mode": "RPC",
        "tool_usage": "0%",
        "spindle_rpm": 0,
        "spindle_torque": 0.0,
        "position": {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0},
        "statusLights": {"controller": "READY", "server": True},
        "ts": now,
    }


def _cutting_payload() -> Dict[str, Any]:
    return {
        "ts": time.time(),
        "feed_rate": 0.0,
        "downfeed_target": 0.0,
        "downfeed_current": 0.0,
        "removal_current": 0.0,
        "removal_expected": 0.0,
        "torque": 0.0,
        "torque_max": 0.0,
        "elapsed_sec": 0.0,
    }


def run_test(args: argparse.Namespace) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    client = ControllerRpcClient(endpoint=args.endpoint, timeout=args.timeout)
    try:
        LOG.info("Pinging RPC endpoint %s ...", args.endpoint)
        if not client.ping():
            LOG.warning("Ping failed (endpoint responded falsy)")
            if args.dry_run:
                return 1

        if args.dry_run:
            LOG.info("Dry run complete.")
            return 0

        status_payload = _status_payload(args.label)
        LOG.info("Pushing status snapshot: %s", status_payload)
        client.push_status(status_payload)

        cutting_payload = _cutting_payload()
        LOG.info("Pushing cutting snapshot: %s", cutting_payload)
        client.push_cutting(cutting_payload)

        LOG.info("RPC test payloads delivered successfully.")
        return 0
    except Exception as exc:  # pragma: no cover - CLI diagnostics
        LOG.error("RPC connectivity test failed: %s", exc, exc_info=True)
        return 2
    finally:
        client.close()


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    code = run_test(args)
    raise SystemExit(code)


if __name__ == "__main__":
    main(sys.argv[1:])
