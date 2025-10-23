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
from app.server.rpc import RpcControlClient, RpcDataStore
from app.server.utils import logs


class RpcBusinessService(BusinessService):
    """Business layer that proxies data/control via gRPC."""

    def __init__(self, store: RpcDataStore, client: RpcControlClient) -> None:
        print("use RpcBusinessService")
        self._store = store
        self._client = client

    async def fetch_status(self) -> StatusModel:
        payload = await asyncio.to_thread(self._store.get_status)
        return StatusModel.from_mapping(payload)

    async def execute_control(self, command: ControlCommand) -> ControlResult:
        try:
            response = await asyncio.to_thread(self._client.handle_control, command.action, command.params)
        except Exception as exc:
            return ControlResult.failure(f"RPC control failed: {exc}", {"error": str(exc)})
        ok = bool(response.get("ok", True))
        message = str(response.get("message", "")) if isinstance(response, dict) else ""
        details = response.get("details", {}) if isinstance(response, dict) else {"raw": response}
        return ControlResult.success(message, details) if ok else ControlResult.failure(message or "Control command rejected", details)

    async def fetch_cutting(self) -> CuttingSnapshot:
        payload = await asyncio.to_thread(self._store.get_cutting)
        return CuttingSnapshot.from_mapping(payload)

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass

    def add_log(self, entry: Dict[str, Any]) -> None:
        level = str(entry.get("level", "INFO"))
        name = str(entry.get("name", "rpc"))
        msg = str(entry.get("msg", entry.get("message", "")))
        ts = entry.get("ts")
        logs.push(level, name, msg, ts=ts if isinstance(ts, (int, float)) else None)
