from __future__ import annotations

import asyncio
import inspect
from typing import Any, Dict, List, Optional

from app.core.state_machine import ProcState
from app.domain.status import get_status_service
from app.devices.motion_base import IMotionController
from app.process.orchestrator import Orchestrator
from app.server.models import ControlCommand, ControlResult, CuttingSnapshot, StatusModel
from app.server.utils import logs

from .base import BusinessService


class RuntimeBusinessService(BusinessService):
    """Business layer backed by real (or production) data sources."""

    def __init__(self, motion: IMotionController, orchestrator: Optional[Orchestrator] = None) -> None:
        self._status_service = get_status_service()
        self._motion = motion
        self._orchestrator = orchestrator

    async def fetch_status(self) -> StatusModel:
        payload = await asyncio.to_thread(self._status_service.fetch_status)
        return StatusModel.from_mapping(payload)

    async def execute_control(self, command: ControlCommand) -> ControlResult:
        action = (command.action or "").strip().lower()
        params = command.params or {}
        if action == "estop":
            return await self._handle_estop()
        if action == "reset":
            return await self._handle_reset()
        if action in {"stop", "run.stop"}:
            return await self._handle_stop()
        if action == "run.start":
            return await self._handle_run_start(params)
        if action in {"motion.home", "home"}:
            return await self._handle_motion_home()
        if action == "motion.set_work_origin":
            return await self._handle_motion_set_work_origin()
        if action == "motion.set_speed":
            return await self._handle_motion_set_speed(params)
        if action == "motion.jog":
            return await self._handle_motion_jog(params)
        return ControlResult.failure(f"Unsupported control action: {command.action}")

    async def _handle_estop(self) -> ControlResult:
        logs.push("WARN", "control", "E-STOP triggered")
        handler = getattr(self._motion, "estop", None)
        if callable(handler):
            try:
                await asyncio.to_thread(handler)
            except Exception as exc:
                logs.push("ERROR", "control", f"E-STOP action failed: {exc}")
                return ControlResult.failure("E-STOP failed", {"error": str(exc)})
        return ControlResult.success("E-STOP acknowledged")

    async def _handle_reset(self) -> ControlResult:
        handler = getattr(self._motion, "home", None)
        if not callable(handler):
            logs.push("INFO", "control", "Reset requested but motion.home missing")
            return ControlResult.failure("Reset unsupported on current motion controller")
        try:
            await asyncio.to_thread(handler)
            logs.push("INFO", "control", "Reset requested -> home sequence completed")
            return ControlResult.success("Reset executed")
        except Exception as exc:
            logs.push("ERROR", "control", f"Reset failed: {exc}")
            return ControlResult.failure("Reset failed", {"error": str(exc)})

    async def _handle_stop(self) -> ControlResult:
        handler = getattr(self._motion, "stop", None)
        if callable(handler):
            try:
                await asyncio.to_thread(handler)
            except Exception as exc:
                logs.push("ERROR", "control", f"Stop failed: {exc}")
                return ControlResult.failure("Stop failed", {"error": str(exc)})
        else:
            if self._orchestrator and hasattr(self._orchestrator, "sm"):
                try:
                    self._orchestrator.sm.state = ProcState.IDLE
                except Exception:
                    pass
        logs.push("INFO", "control", "Soft stop requested")
        return ControlResult.success("Stop acknowledged")

    async def _handle_run_start(self, params: Dict[str, Any]) -> ControlResult:
        logs.push("INFO", "control", f"Run start requested params={params!r}")
        if self._orchestrator is None:
            return ControlResult.success("Run start accepted")
        start_fn = getattr(self._orchestrator, "start", None)
        if callable(start_fn):
            call_args: List[Any] = []
            try:
                signature = inspect.signature(start_fn)
                required = [
                    param
                    for param in signature.parameters.values()
                    if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                    and param.default is inspect._empty
                ]
                if required:
                    call_args.append(params)
            except (ValueError, TypeError):
                if params:
                    call_args.append(params)
            try:
                await asyncio.to_thread(start_fn, *call_args)
            except Exception as exc:
                logs.push("ERROR", "control", f"Run start failed via orchestrator.start: {exc}")
                return ControlResult.failure("Run start failed", {"error": str(exc)})
            logs.push("INFO", "control", "Run start invoked on orchestrator")
            return ControlResult.success("Run start triggered")
        sm = getattr(self._orchestrator, "sm", None)
        if sm is not None:
            try:
                sm.state = ProcState.LOCATE
                logs.push("INFO", "control", "Run state machine transitioned to LOCATE")
                return ControlResult.success("Run state machine advanced to LOCATE")
            except Exception as exc:
                logs.push("ERROR", "control", f"Run start failed while updating state machine: {exc}")
                return ControlResult.failure("Run start failed", {"error": str(exc)})
        return ControlResult.success("Run start accepted")

    async def _handle_motion_home(self) -> ControlResult:
        return await self._invoke_motion("home", "Home sequence completed")

    async def _handle_motion_set_work_origin(self) -> ControlResult:
        return await self._invoke_motion("set_work_origin", "Work origin updated")

    async def _handle_motion_set_speed(self, params: Dict[str, Any]) -> ControlResult:
        try:
            v_fast = float(params.get("v_fast"))
            v_work = float(params.get("v_work"))
        except (TypeError, ValueError):
            logs.push("WARN", "control", f"Invalid set_speed parameters: {params!r}")
            return ControlResult.failure("Invalid speed parameters", {"params": dict(params)})
        return await self._invoke_motion(
            "set_speed",
            f"Motion speed updated (v_fast={v_fast}, v_work={v_work})",
            v_fast,
            v_work,
        )

    async def _handle_motion_jog(self, params: Dict[str, Any]) -> ControlResult:
        axis = str(params.get("axis", "")).strip()
        if not axis:
            logs.push("WARN", "control", f"Jog rejected due to missing axis: {params!r}")
            return ControlResult.failure("Axis is required for jog command")
        try:
            direction = int(params.get("direction", 0))
        except (TypeError, ValueError):
            logs.push("WARN", "control", f"Jog rejected due to invalid direction: {params!r}")
            return ControlResult.failure("Invalid jog direction")
        speed_value = params.get("speed", 10.0)
        try:
            speed = float(speed_value)
        except (TypeError, ValueError):
            logs.push("WARN", "control", f"Jog rejected due to invalid speed: {params!r}")
            return ControlResult.failure("Invalid jog speed")
        return await self._invoke_motion(
            "jog",
            f"Jog executed on axis {axis}",
            axis,
            direction,
            speed,
        )

    async def _invoke_motion(self, method: str, success_message: str, *args: Any) -> ControlResult:
        handler = getattr(self._motion, method, None)
        if not callable(handler):
            logs.push("WARN", "control", f"Motion handler missing method={method}")
            return ControlResult.failure(f"Motion controller does not support {method.replace('_', ' ')}")
        try:
            await asyncio.to_thread(handler, *args)
        except Exception as exc:
            logs.push("ERROR", "control", f"Motion handler {method} failed: {exc}")
            return ControlResult.failure(f"{method.replace('_', ' ').title()} failed", {"error": str(exc)})
        logs.push("INFO", "control", f"Motion handler {method} executed")
        return ControlResult.success(success_message)

    async def fetch_cutting(self) -> CuttingSnapshot:
        provider = getattr(self._status_service, "fetch_cutting", None)
        if callable(provider):
            try:
                payload = await asyncio.to_thread(provider)
                if isinstance(payload, CuttingSnapshot):
                    return payload
                return CuttingSnapshot.from_mapping(payload)
            except Exception:
                pass

        if self._orchestrator is not None:
            builder = getattr(self._orchestrator, "get_cutting_snapshot", None)
            if callable(builder):
                try:
                    payload = await asyncio.to_thread(builder)
                    if isinstance(payload, CuttingSnapshot):
                        return payload
                    return CuttingSnapshot.from_mapping(payload)
                except Exception:
                    pass

        return CuttingSnapshot()

    def add_log(self, entry: Dict[str, Any]) -> None:
        level = str(entry.get("level", "INFO"))
        name = str(entry.get("name", "runtime"))
        msg = str(entry.get("msg", entry.get("message", "")))
        ts = entry.get("ts")
        logs.push(level, name, msg, ts=ts if isinstance(ts, (int, float)) else None)
