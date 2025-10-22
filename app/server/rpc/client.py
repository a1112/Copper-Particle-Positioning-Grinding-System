from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Mapping, Optional

log = logging.getLogger("app.rpc.client")


def _load_zerorpc():
    try:
        import zerorpc  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("zerorpc is not installed. Please install the optional rpc extras.") from exc
    return zerorpc


class RpcControlClient:
    """Lazy ZeroRPC client used to dispatch control commands to the controller."""

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
            log.info("ZeroRPC control client connected to %s", self._endpoint)
            return client

    def _reset(self) -> None:
        with self._lock:
            client = self._client
            self._client = None
        if client is not None:
            try:
                client.close()
            except Exception:  # pragma: no cover - best-effort cleanup
                pass

    def handle_control(self, action: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(params or {})
        client = self._ensure_client()
        try:
            response = client.handle_control(action, payload)  # type: ignore[attr-defined]
        except Exception as exc:
            log.error("ZeroRPC control call failed: %s", exc)
            self._reset()
            raise
        if not isinstance(response, dict):
            return {"ok": bool(response), "raw": response}
        return response

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
