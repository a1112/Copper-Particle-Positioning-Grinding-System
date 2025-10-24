from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Any, AsyncIterator, Iterable, List
from urllib.parse import urlparse

from app.controller.httpbridge import HttpControllerService
from app.controller.rpc.service import RpcControllerService

from .publisher import publish_scenario
from .scenarios import Scenario, load_scenarios

LOG = logging.getLogger("controller")


async def cycle_scenarios(scenarios: Iterable[Scenario], loop: bool) -> AsyncIterator[Scenario]:
    cached: List[Scenario] = list(scenarios)
    while True:
        for scenario in cached:
            yield scenario
        if not loop:
            break


async def run_controller(args: argparse.Namespace) -> None:
    paths = [Path(item) for item in args.scenario]
    scenarios = load_scenarios(paths)

    transport = args.transport.lower()
    service: Any
    if transport == "http":
        parsed = urlparse(args.http_control)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 9001
        service = HttpControllerService(
            base_url=args.http_base,
            control_host=host,
            control_port=port,
            timeout=args.http_timeout,
        )
        label = f"HTTP (bridge={args.http_base}, control={args.http_control})"
    else:
        service = RpcControllerService(
            listen_endpoint=args.rpc_listen,
            server_endpoint=args.rpc_server,
            timeout=args.rpc_timeout,
        )
        label = f"gRPC (listen={args.rpc_listen}, upstream={args.rpc_server})"

    service.start()
    LOG.info("Controller started using %s", label)

    try:
        if not service.ping():
            LOG.warning("Initial transport ping failed; continuing regardless")
        async for scenario in cycle_scenarios(scenarios, args.loop):
            publish_scenario(service, scenario)
            await asyncio.sleep(scenario.delay if args.respect_delay else args.interval)
    finally:
        service.stop()
        LOG.info("Controller stopped")
