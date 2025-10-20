from __future__ import annotations

import asyncio
from typing import List, Optional

from app.domain.status import get_status_service
from app.server.models import ControlCommand, ControlResult, LogEntry, StatusModel
from app.server.utils import logs

from .base import BusinessService


class SimBusinessService(BusinessService):
    """Business layer backed by simulator data sources."""

    def __init__(self) -> None:
        self._status_service = get_status_service()

    async def fetch_status(self) -> StatusModel:
        payload = await asyncio.to_thread(self._status_service.fetch_status)
        return StatusModel.from_mapping(payload)

    async def fetch_logs(self, limit: Optional[int] = None) -> List[LogEntry]:
        entries = await asyncio.to_thread(logs.as_list)
        if limit is not None and limit >= 0:
            entries = entries[-limit:]
        return [LogEntry.from_mapping(item) for item in entries]

    async def execute_control(self, command: ControlCommand) -> ControlResult:
        logs.push("INFO", "control", f"[sim] command={command.action}")
        return ControlResult.success(message="Simulated control executed", details={"action": command.action})
