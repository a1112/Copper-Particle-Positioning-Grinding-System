from __future__ import annotations

import logging
from typing import Dict, Optional

from app.devices.motion_base import IMotionController
from app.devices.sim.virtual_parameter_device import VirtualParameterDevice

from .path_planning import ToolPath
from .sim_path_planner import SimulatedPathPlanner, SimulatedPlan

LOGGER = logging.getLogger(__name__)


class SimulatedProcessExecutor:
    """High-level simulator that converts planned paths into motion commands."""

    def __init__(
        self,
        motion: IMotionController,
        planner: SimulatedPathPlanner,
        parameter_device: VirtualParameterDevice,
    ) -> None:
        self.motion = motion
        self.planner = planner
        self.parameter_device = parameter_device
        self._last_plan: Optional[SimulatedPlan] = None

    @property
    def last_plan(self) -> Optional[SimulatedPlan]:
        return self._last_plan

    def execute_path(self, tool_path: ToolPath, *, wait: bool = True) -> None:
        """Traverse the tool path with the motion simulator."""
        for segment in tool_path.segments:
            pts = segment.pts or []
            for x, y, z in pts:
                try:
                    self.motion.move_abs(float(x), float(y), float(z))
                except Exception:  # pragma: no cover - defensive safeguard
                    LOGGER.exception("Simulated motion failed at point (%s, %s, %s)", x, y, z)
            if wait:
                try:
                    self.motion.wait_done()
                except Exception:  # pragma: no cover - defensive safeguard
                    LOGGER.exception("Simulated wait_done failed for segment %s", segment.kind)

    def plan(self, **kwargs) -> SimulatedPlan:
        """Generate a demo plan using the underlying planner."""
        plan = self.planner.demo_plan(**kwargs)
        self._last_plan = plan
        return plan

    def plan_and_record(self, *, execute: bool = False, **kwargs) -> Dict[str, float]:
        """Plan a path, optionally execute, and return the summary."""
        plan = self.plan(**kwargs)
        if execute:
            self.execute_path(plan.path)
        self.parameter_device.update_path_summary(plan.summary)
        return plan.summary

    def plan_execute_and_record(self, *, execute: bool = True, **kwargs) -> Dict[str, float]:
        """Full simulation cycle: plan, optionally execute, and publish telemetry."""
        plan = self.plan(**kwargs)
        if execute:
            self.execute_path(plan.path)
        self.parameter_device.update_path_summary(plan.summary)
        return plan.summary