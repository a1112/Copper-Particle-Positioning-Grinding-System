from __future__ import annotations

import logging
from typing import Any

from .scenarios import Scenario

LOG = logging.getLogger("controller.publisher")


def publish_scenario(service: Any, scenario: Scenario) -> None:
    """Send one scenario to the downstream service."""

    status_payload = dict(scenario.status)
    status_payload.setdefault("label", scenario.name)
    ok_status = service.publish_status(status_payload)
    LOG.info("Published status snapshot %s (ok=%s)", scenario.name, ok_status)

    if scenario.cutting:
        ok_cutting = service.publish_cutting(scenario.cutting)
        LOG.info("Published cutting snapshot %s (ok=%s)", scenario.name, ok_cutting)
    if scenario.program is not None:
        program_payload = {"program": list(scenario.program)}
        if scenario.program_state:
            program_payload["program_state"] = dict(scenario.program_state)
        publish_program = getattr(service, "publish_program", None)
        if callable(publish_program):
            ok_program = publish_program(program_payload)
            LOG.info(
                "Published program snapshot %s (ok=%s lines=%d)",
                scenario.name,
                ok_program,
                len(scenario.program),
            )
        else:
            LOG.debug("Service %s does not support program publishing", service.__class__.__name__)
    if scenario.logs:
        ok_logs = service.publish_logs(scenario.logs)
        LOG.info("Published %d log entries (ok=%s)", len(scenario.logs), ok_logs)
