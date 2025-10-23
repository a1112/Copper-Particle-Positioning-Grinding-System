from __future__ import annotations

import logging
import threading
from typing import Any, Iterable, Mapping, Optional

import httpx

log = logging.getLogger("controller.http.client")


class HttpControllerClient:
    """Client that pushes telemetry snapshots to the API server via HTTP bridge."""

    def __init__(self, *, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._lock = threading.RLock()
        self._client: Optional[httpx.Client] = None

    def _ensure_client(self) -> httpx.Client:
        with self._lock:
            if self._client is not None:
                return self._client
            self._client = httpx.Client(timeout=self._timeout)
            log.info("Controller HTTP client targeting %s", self._base_url)
            return self._client

    def _reset(self) -> None:
        with self._lock:
            client = self._client
            self._client = None
        if client is not None:
            try:
                client.close()
            except Exception:  # pragma: no cover - best-effort
                pass

    def push_status(self, payload: Mapping[str, Any]) -> bool:
        client = self._ensure_client()
        try:
            response = client.post(f"{self._base_url}/status", json=dict(payload or {}))
            response.raise_for_status()
        except Exception as exc:
            log.error("push_status failed: %s", exc)
            self._reset()
            raise
        return bool(response.json().get("ok", True))

    def push_cutting(self, payload: Mapping[str, Any]) -> bool:
        client = self._ensure_client()
        try:
            response = client.post(f"{self._base_url}/cutting", json=dict(payload or {}))
            response.raise_for_status()
        except Exception as exc:
            log.error("push_cutting failed: %s", exc)
            self._reset()
            raise
        return bool(response.json().get("ok", True))

    def push_logs(self, entries: Iterable[Mapping[str, Any]]) -> bool:
        client = self._ensure_client()
        try:
            response = client.post(f"{self._base_url}/logs", json=list(entries))
            response.raise_for_status()
        except Exception as exc:
            log.error("push_logs failed: %s", exc)
            self._reset()
            raise
        return bool(response.json().get("ok", True))

    def ping(self) -> bool:
        client = self._ensure_client()
        try:
            response = client.get(f"{self._base_url}/ping")
            response.raise_for_status()
        except Exception as exc:
            log.debug("HTTP ping failed: %s", exc)
            self._reset()
            return False
        data = response.json()
        if isinstance(data, dict):
            return bool(data.get("ok", True))
        return bool(data)

    def close(self) -> None:
        self._reset()

