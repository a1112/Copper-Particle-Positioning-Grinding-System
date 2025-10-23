from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from app.server.models import (
    ControlCommand,
    ControlResult,
    CuttingSnapshot,
    LogEntry,
    StatusModel,
    ToolInfoSnapshot,
)

from .base import BusinessService
from .tool_info import ToolInfoAssembler
from app.server.httpbridge.client import HttpControlClient
from app.server.httpbridge.store import HttpDataStore


class HttpBusinessService(BusinessService):
    """Business layer that proxies data/control via HTTP bridge."""

    def __init__(self, store: HttpDataStore, client: HttpControlClient) -> None:
        self._store = store
        self._client = client
        self._tool_info = ToolInfoAssembler()

    async def fetch_status(self) -> StatusModel:
        payload = await asyncio.to_thread(self._store.get_status)
        return StatusModel.from_mapping(payload)

    async def fetch_logs(self, limit: Optional[int] = None) -> List[LogEntry]:
        entries = await asyncio.to_thread(self._store.get_logs)
        if isinstance(entries, list):
            raw_entries = entries
        else:
            raw_entries = list(entries)
        if limit is not None and limit >= 0:
            raw_entries = raw_entries[-limit:]
        return [LogEntry.from_mapping(item) for item in raw_entries]

    async def execute_control(self, command: ControlCommand) -> ControlResult:
        try:
            response = await self._client.handle_control(command.action, command.params)
        except Exception as exc:
            return ControlResult.failure(f"HTTP control failed: {exc}", {"error": str(exc)})
        ok = bool(response.get("ok", True))
        message = str(response.get("message", "")) if isinstance(response, dict) else ""
        details = response.get("details", {}) if isinstance(response, dict) else {"raw": response}
        return ControlResult.success(message, details) if ok else ControlResult.failure(message or "Control command rejected", details)

    async def fetch_cutting(self) -> CuttingSnapshot:
        payload = await asyncio.to_thread(self._store.get_cutting)
        return CuttingSnapshot.from_mapping(payload)

    async def fetch_tool_info(self) -> ToolInfoSnapshot:
        status_payload = await asyncio.to_thread(self._store.get_status)
        return await asyncio.to_thread(self._tool_info.build, status_payload)

    async def close(self) -> None:
        try:
            await self._client.close()
        except Exception:
            pass

