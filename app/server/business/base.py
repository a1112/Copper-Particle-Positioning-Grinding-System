from __future__ import annotations

import abc
from typing import List, Optional

from app.server.models import ControlCommand, ControlResult, LogEntry, StatusModel


class BusinessService(abc.ABC):
    """Abstract interface describing business capabilities exposed to the API."""

    @abc.abstractmethod
    async def fetch_status(self) -> StatusModel:
        """Return the latest machine status snapshot."""

    @abc.abstractmethod
    async def fetch_logs(self, limit: Optional[int] = None) -> List[LogEntry]:
        """Obtain recent log entries ordered from oldest to newest."""

    @abc.abstractmethod
    async def execute_control(self, command: ControlCommand) -> ControlResult:
        """Execute a control command emitted by the API."""
