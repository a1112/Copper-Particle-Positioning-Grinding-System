from __future__ import annotations

import logging
import threading
from typing import Any, Iterable, Mapping, Optional

import requests

log = logging.getLogger("controller.httpbridge.client")


class HttpControllerClient:
    """Client that pushes telemetry snapshots to the API server via HTTP bridge."""

    def __init__(self, *, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._lock = threading.RLock()
        self._session: Optional[requests.Session] = None

    def _ensure_session(self) -> requests.Session:
        with self._lock:
            if self._session is not None:
                return self._session
            session = requests.Session()
            session.trust_env = False
            session.headers.update({"User-Agent": "http-sim"})
            self._session = session
            log.info("Controller HTTP bridge client targeting %s", self._base_url)
            return session

    def _reset(self) -> None:
        with self._lock:
            session = self._session
            self._session = None
        if session is not None:
            try:
                session.close()
            except Exception:  # pragma: no cover - best-effort cleanup
                pass

    def _request(self, method: str, path: str, *, json_payload: Any = None) -> requests.Response:
        session = self._ensure_session()
        url = f"{self._base_url}{path}"
        try:
            response = session.request(method, url, json=json_payload, timeout=self._timeout)
            response.raise_for_status()
        except requests.HTTPError as exc:
            body = exc.response.text if exc.response is not None else ""
            log.error("HTTP %s %s failed (%s): %s", method.upper(), url, exc.response.status_code if exc.response else "n/a", body)
            self._reset()
            raise
        except requests.RequestException as exc:
            log.error("HTTP %s %s transport error: %s", method.upper(), url, exc)
            self._reset()
            raise
        return response

    def push_status(self, payload: Mapping[str, Any]) -> bool:
        response = self._request("post", "/status", json_payload=dict(payload or {}))
        data = response.json()
        return bool(data.get("ok", True) if isinstance(data, dict) else data)

    def push_cutting(self, payload: Mapping[str, Any]) -> bool:
        response = self._request("post", "/cutting", json_payload=dict(payload or {}))
        data = response.json()
        return bool(data.get("ok", True) if isinstance(data, dict) else data)

    def push_logs(self, entries: Iterable[Mapping[str, Any]]) -> bool:
        response = self._request("post", "/logs", json_payload=list(entries))
        data = response.json()
        return bool(data.get("ok", True) if isinstance(data, dict) else data)

    def ping(self) -> bool:
        try:
            response = self._request("get", "/ping")
        except Exception:
            return False
        data = response.json()
        return bool(data.get("ok", True) if isinstance(data, dict) else data)

    def close(self) -> None:
        self._reset()
