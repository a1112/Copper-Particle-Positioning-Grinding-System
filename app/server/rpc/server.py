from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional

from .store import RpcDataStore

log = logging.getLogger("app.rpc.server")

try:  # pragma: no cover - optional dependency guard
    import gevent  # type: ignore
except ImportError:
    gevent = None  # type: ignore[assignment]


def _load_zerorpc():
    try:
        import zerorpc  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("zerorpc is not installed. Please install the optional rpc extras.") from exc
    return zerorpc


class RpcDataReceiver:
    """ZeroRPC handler exposing endpoints for controller components."""

    def __init__(self, store: RpcDataStore) -> None:
        self._store = store

    def push_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._store.update_status(payload or {})
        return {"ok": True}

    def push_cutting(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._store.update_cutting(payload or {})
        return {"ok": True}

    def push_logs(self, entries: Any) -> Dict[str, Any]:
        if isinstance(entries, dict):
            self._store.append_log(entries)
        else:
            try:
                iterator = list(entries)  # exhaust generators before lock
            except TypeError:
                self._store.append_log({"message": str(entries)})
            else:
                self._store.extend_logs(iterator)
        return {"ok": True}

    def ping(self) -> bool:
        return True


class RpcServerRunner:
    """Background ZeroRPC server bound to an endpoint."""

    def __init__(self, *, endpoint: str, store: RpcDataStore) -> None:
        self._endpoint = endpoint
        self._store = store
        self._server = None
        self._thread: Optional[threading.Thread] = None
        self._greenlet = None

    def start(self) -> None:
        if self._server is not None:
            return
        zerorpc = _load_zerorpc()
        receiver = RpcDataReceiver(self._store)
        server = zerorpc.Server(receiver)
        server.bind(self._endpoint)

        def _run() -> None:
            log.info("ZeroRPC server listening at %s", self._endpoint)
            try:
                server.run()
            except Exception as exc:  # pragma: no cover - background guard
                log.error("ZeroRPC server stopped unexpectedly: %s", exc)

        self._server = server
        if gevent is not None:
            self._greenlet = gevent.spawn(_run)
        else:  # pragma: no cover - fallback when gevent is unavailable
            thread = threading.Thread(target=_run, name="rpc-server", daemon=True)
            thread.start()
            self._thread = thread

    def stop(self) -> None:
        server = self._server
        if server is None:
            return
        try:
            server.stop()
        except Exception as exc:  # pragma: no cover - best-effort shutdown
            log.warning("Failed to stop ZeroRPC server cleanly: %s", exc)
        self._server = None
        if self._greenlet is not None:
            try:
                self._greenlet.kill()
            except Exception:  # pragma: no cover - best effort
                pass
            self._greenlet = None
        self._thread = None
