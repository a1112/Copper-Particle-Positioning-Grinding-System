from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional

from app.server.models import (
    ControlCommand,
    ControlResult,
    CuttingSnapshot,
    LogEntry,
    StatusModel,
    ToolInfoSnapshot,
)


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

    @abc.abstractmethod
    async def fetch_cutting(self) -> CuttingSnapshot:
        """Return the latest cutting telemetry snapshot."""

    async def apply_cutting_override(self, payload: Dict[str, Any], *, merge: bool = False) -> Dict[str, Any]:
        """Update manual cutting overrides (optional)."""
        raise NotImplementedError("Cutting overrides are not supported by this backend")

    async def get_cutting_override(self) -> Dict[str, Any]:
        """Return active manual cutting overrides (optional)."""
        raise NotImplementedError("Cutting overrides are not supported by this backend")

    async def clear_cutting_override(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Clear manual cutting overrides (optional)."""
        raise NotImplementedError("Cutting overrides are not supported by this backend")

    async def fetch_tool_info(self) -> ToolInfoSnapshot:
        """Return structured tool information (optional)."""
        raise NotImplementedError("Tool info retrieval is not supported by this backend")
