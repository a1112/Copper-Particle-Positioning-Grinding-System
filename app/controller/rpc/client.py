from __future__ import annotations

import logging
import threading
from typing import Any, Iterable, Mapping, Optional

log = logging.getLogger("controller.rpc.client")


def _load_zerorpc():
    try:
        import zerorpc  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - optional dependency guard
        raise RuntimeError("zerorpc is not installed. Install zerorpc to use the RPC controller mode.") from exc
    return zerorpc


class ControllerRpcClient:
    """Client that pushes telemetry snapshots to the API server via ZeroRPC."""

    def __init__(self, *, endpoint: str, timeout: float = 5.0) -> None:
        self._endpoint = endpoint
        self._timeout = timeout
        self._lock = threading.RLock()
        self._client = None

    def _ensure_client(self):
        with self._lock:
            if self._client is not None:
                return self._client
            zerorpc = _load_zerorpc()
            client = zerorpc.Client(timeout=self._timeout)
            client.connect(self._endpoint)
            self._client = client
            log.info("Controller ZeroRPC client connected to %s", self._endpoint)
            return client

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
            response = client.push_status(dict(payload or {}))  # type: ignore[attr-defined]
        except Exception as exc:
            log.error("push_status failed: %s", exc)
            self._reset()
            raise
        return bool(getattr(response, "get", lambda *_: False)("ok", True))

    def push_cutting(self, payload: Mapping[str, Any]) -> bool:
        client = self._ensure_client()
        try:
            response = client.push_cutting(dict(payload or {}))  # type: ignore[attr-defined]
        except Exception as exc:
            log.error("push_cutting failed: %s", exc)
            self._reset()
            raise
        return bool(getattr(response, "get", lambda *_: False)("ok", True))

    def push_logs(self, entries: Iterable[Mapping[str, Any]]) -> bool:
        client = self._ensure_client()
        try:
            response = client.push_logs(list(entries))  # type: ignore[attr-defined]
        except Exception as exc:
            log.error("push_logs failed: %s", exc)
            self._reset()
            raise
        return bool(getattr(response, "get", lambda *_: False)("ok", True))

    def ping(self) -> bool:
        client = self._ensure_client()
        try:
            result = client.ping()  # type: ignore[attr-defined]
            return bool(result)
        except Exception as exc:
            log.debug("ZeroRPC ping failed: %s", exc)
            self._reset()
            return False

    def close(self) -> None:
        self._reset()
