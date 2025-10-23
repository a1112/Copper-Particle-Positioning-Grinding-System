from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any, Mapping, Optional

import requests

log = logging.getLogger("app.httpbridge.client")


class HttpControlClient:
    """HTTP client used to dispatch control commands to the controller process."""

    def __init__(self, *, endpoint: str, timeout: float = 5.0) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._timeout = timeout
        self._lock = threading.RLock()
        self._session: Optional[requests.Session] = None

    def _ensure_session(self) -> requests.Session:
        with self._lock:
            if self._session is not None:
                return self._session
            session = requests.Session()
            session.trust_env = False
            session.headers.update({"User-Agent": "http-control"})
            self._session = session
            log.info("HTTP control client configured for %s", self._endpoint)
            return session

    def _sync_request(self, method: str, *, json_payload: Any = None, params: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        session = self._ensure_session()
        try:
            response = session.request(
                method,
                self._endpoint,
                json=json_payload,
                params=params,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            body = exc.response.text if exc.response is not None else ""
            status = exc.response.status_code if exc.response is not None else "n/a"
            log.error("HTTP %s %s failed (%s): %s", method.upper(), self._endpoint, status, body)
            raise
        except requests.RequestException as exc:
            log.error("HTTP %s %s transport error: %s", method.upper(), self._endpoint, exc)
            raise
        payload = response.json()
        if isinstance(payload, Mapping):
            return dict(payload)
        return {"ok": bool(payload), "raw": payload}

    async def handle_control(self, action: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
        payload = {"action": action, "params": dict(params or {})}
        data = await asyncio.to_thread(self._sync_request, "post", json_payload=payload)
        data.setdefault("ok", True)
        return data

    async def ping(self) -> bool:
        try:
            data = await asyncio.to_thread(self._sync_request, "get", params={"action": "ping"})
        except Exception as exc:
            log.debug("HTTP control ping failed: %s", exc)
            return False
        return bool(data.get("ok", True))

    async def close(self) -> None:
        with self._lock:
            session = self._session
            self._session = None
        if session is not None:
            await asyncio.to_thread(session.close)
