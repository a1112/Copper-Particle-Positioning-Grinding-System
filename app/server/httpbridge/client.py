from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

import httpx

log = logging.getLogger("app.httpbridge.client")


class HttpControlClient:
    """HTTP client used to dispatch control commands to the controller process."""

    def __init__(self, *, endpoint: str, timeout: float = 5.0) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        self._client = httpx.AsyncClient(timeout=self._timeout)
        log.info("HTTP control client configured for %s", self._endpoint)
        return self._client

    async def handle_control(self, action: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
        payload = {"action": action, "params": dict(params or {})}
        client = await self._ensure_client()
        try:
            response = await client.post(self._endpoint, json=payload)
            response.raise_for_status()
        except Exception as exc:
            log.error("HTTP control call failed: %s", exc)
            raise
        data = response.json()
        if not isinstance(data, dict):
            return {"ok": bool(data), "raw": data}
        data.setdefault("ok", True)
        return data

    async def ping(self) -> bool:
        client = await self._ensure_client()
        try:
            response = await client.get(self._endpoint, params={"action": "ping"})
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            log.debug("HTTP control ping failed: %s", exc)
            return False
        if isinstance(data, dict):
            return bool(data.get("ok", True))
        return bool(data)

    async def close(self) -> None:
        client = self._client
        self._client = None
        if client is not None:
            await client.aclose()

