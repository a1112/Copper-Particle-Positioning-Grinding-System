from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from app.server.models import (
    ControlCommand,
    ControlResult,
    CuttingSnapshot,
    StatusModel,
)

from .base import BusinessService
from app.server.httpbridge.client import HttpControlClient
from app.server.httpbridge.store import HttpDataStore
from app.server.utils import logs


class HttpBusinessService(BusinessService):
    """Business layer that proxies data/control via HTTP bridge."""

    def __init__(self, store: HttpDataStore, client: HttpControlClient) -> None:
        self._store = store
        self._client = client

    async def fetch_status(self) -> StatusModel:
        payload = await asyncio.to_thread(self._store.get_status)
        return StatusModel.from_mapping(payload)

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

    async def close(self) -> None:
        try:
            await self._client.close()
        except Exception:
            pass

    def add_log(self, entry: Dict[str, Any]) -> None:
        level = str(entry.get("level", "INFO"))
        name = str(entry.get("name", "http"))
        msg = str(entry.get("msg", entry.get("message", "")))
        ts = entry.get("ts")
        logs.push(level, name, msg, ts=ts if isinstance(ts, (int, float)) else None)
