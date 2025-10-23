from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from app.core.state_machine import ProcState
from app.domain.status import get_status_service
from app.devices.motion_base import IMotionController
from app.process.orchestrator import Orchestrator
from app.server.models import ControlCommand, ControlResult, CuttingSnapshot, StatusModel, ToolInfoSnapshot
from app.server.utils import logs

from .base import BusinessService
from .tool_info import ToolInfoAssembler


class RuntimeBusinessService(BusinessService):
    """Business layer backed by real (or production) data sources."""

    def __init__(self, motion: IMotionController, orchestrator: Optional[Orchestrator] = None) -> None:
        self._status_service = get_status_service()
        self._motion = motion
        self._orchestrator = orchestrator
        self._tool_info = ToolInfoAssembler()

    async def fetch_status(self) -> StatusModel:
        payload = await asyncio.to_thread(self._status_service.fetch_status)
        return StatusModel.from_mapping(payload)

    async def execute_control(self, command: ControlCommand) -> ControlResult:
        action = command.action.lower()
        if action == "estop":
            return await self._handle_estop()
        if action == "reset":
            return await self._handle_reset()
        if action == "stop":
            return await self._handle_stop()
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

    async def fetch_tool_info(self) -> ToolInfoSnapshot:
        status_payload = await asyncio.to_thread(self._status_service.fetch_status)
        return await asyncio.to_thread(self._tool_info.build, status_payload)

    def add_log(self, entry: Dict[str, Any]) -> None:
        level = str(entry.get("level", "INFO"))
        name = str(entry.get("name", "runtime"))
        msg = str(entry.get("msg", entry.get("message", "")))
        ts = entry.get("ts")
        logs.push(level, name, msg, ts=ts if isinstance(ts, (int, float)) else None)
