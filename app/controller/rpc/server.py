from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Mapping, Optional

log = logging.getLogger("controller.rpc.server")

try:  # pragma: no cover - optional dependency guard
    import gevent  # type: ignore
except ImportError:
    gevent = None  # type: ignore[assignment]


def _load_zerorpc():
    try:
        import zerorpc  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("zerorpc is not installed. Install zerorpc to use the RPC controller mode.") from exc
    return zerorpc


ControlCallback = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


class _ControllerRpcHandler:
    def __init__(self, callback: ControlCallback) -> None:
        self._callback = callback

    def handle_control(self, action: str, params: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
        try:
            return dict(self._callback(action, dict(params or {})))
        except Exception as exc:  # pragma: no cover - remote errors surface to caller
            log.exception("Control handler failure for action=%s: %s", action, exc)
            return {"ok": False, "error": str(exc)}

    def ping(self) -> bool:
        return True


class ControllerRpcServer:
    """ZeroRPC server running inside the controller process to receive commands."""

    def __init__(self, *, endpoint: str, callback: ControlCallback) -> None:
        self._endpoint = endpoint
        self._callback = callback
        self._server = None
        self._thread: Optional[threading.Thread] = None
        self._greenlet = None

    def start(self) -> None:
        if self._server is not None:
            return
        zerorpc = _load_zerorpc()
        handler = _ControllerRpcHandler(self._callback)
        server = zerorpc.Server(handler)
        server.bind(self._endpoint)

        def _run() -> None:
            log.info("Controller ZeroRPC server listening at %s", self._endpoint)
            try:
                server.run()
            except Exception as exc:  # pragma: no cover - background guard
                log.error("Controller ZeroRPC server crashed: %s", exc)

        self._server = server
        if gevent is not None:
            self._greenlet = gevent.spawn(_run)
        else:  # pragma: no cover - fallback when gevent unavailable
            thread = threading.Thread(target=_run, name="controller-rpc", daemon=True)
            thread.start()
            self._thread = thread

    def stop(self) -> None:
        server = self._server
        if server is None:
            return
        try:
            server.stop()
        except Exception as exc:  # pragma: no cover - best-effort cleanup
            log.warning("Failed to stop Controller ZeroRPC server cleanly: %s", exc)
        self._server = None
        if self._greenlet is not None:
            try:
                self._greenlet.kill()
            except Exception:  # pragma: no cover - best effort
                pass
            self._greenlet = None
        self._thread = None
