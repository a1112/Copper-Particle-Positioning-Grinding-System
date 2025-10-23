from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

from .client import ControllerRpcClient
from .server import ControllerRpcServer

log = logging.getLogger("controller.rpc.service")

ControlHandler = Callable[[str, Dict[str, Any]], Mapping[str, Any]]


class RpcControllerService:
    """High-level helper binding the controller logic to the API server via gRPC."""

    def __init__(
        self,
        *,
        listen_endpoint: str,
        server_endpoint: str,
        timeout: float = 5.0,
    ) -> None:
        self._client = ControllerRpcClient(endpoint=server_endpoint, timeout=timeout)
        self._handlers: List[ControlHandler] = []
        self._server = ControllerRpcServer(endpoint=listen_endpoint, callback=self._dispatch_control)

    def start(self) -> None:
        """Start the inbound gRPC server so control commands can be received."""
        self._server.start()

    def stop(self) -> None:
        """Stop the inbound server and close the outbound client."""
        try:
            self._server.stop()
        finally:
            self._client.close()

    def register_control_handler(self, handler: ControlHandler) -> None:
        """Register a callable that will process incoming control commands."""
        self._handlers.append(handler)

    def publish_status(self, payload: Mapping[str, Any]) -> bool:
        return self._client.push_status(payload)

    def publish_cutting(self, payload: Mapping[str, Any]) -> bool:
        return self._client.push_cutting(payload)

    def publish_logs(self, entries: Iterable[Mapping[str, Any]]) -> bool:
        return self._client.push_logs(entries)

    def ping(self) -> bool:
        return self._client.ping()

    def _dispatch_control(self, action: str, params: Dict[str, Any]) -> Mapping[str, Any]:
        log.info("Received RPC control dispatch action=%s params=%s", action, dict(params))
        if not self._handlers:
            log.warning("No control handlers registered; ignoring action=%s", action)
            return {"ok": False, "message": "No handlers registered"}
        for handler in self._handlers:
            handler_name = getattr(handler, "__name__", handler.__class__.__name__)
            log.debug("Invoking RPC control handler=%s action=%s", handler_name, action)
            try:
                response = handler(action, params)
            except Exception as exc:  # pragma: no cover - surfaced to server
                log.exception("Control handler %s raised an exception: %s", handler_name, exc)
                continue
            if response:
                mapped = dict(response)
                mapped.setdefault("ok", True)
                log.info(
                    "RPC control handler response handler=%s action=%s ok=%s message=%s",
                    handler_name,
                    action,
                    mapped.get("ok", True),
                    mapped.get("message", ""),
                )
                return mapped
            log.debug("RPC control handler %s returned empty response for action=%s", handler_name, action)
        log.warning("All RPC handlers rejected control request action=%s", action)
        return {"ok": False, "message": "All handlers rejected request"}
