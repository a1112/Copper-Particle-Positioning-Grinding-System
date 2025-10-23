from __future__ import annotations

import logging
import threading
from concurrent import futures
from typing import Any, Callable, Dict, Mapping, Optional

import grpc

from app.rpc.common import (
    coerce_mapping,
    deserialize_json,
    normalize_endpoint,
    serialize_json,
)

log = logging.getLogger("controller.rpc.server")

ControlCallback = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


class _ControllerRpcHandler:
    def __init__(self, callback: ControlCallback) -> None:
        self._callback = callback

    def HandleControl(self, request, context):  # noqa: N802 - gRPC signature
        del context
        payload = coerce_mapping(request)
        action = str(payload.get("action", ""))
        params = coerce_mapping(payload.get("params"))
        try:
            response = dict(self._callback(action, params))
        except Exception as exc:  # pragma: no cover - remote errors surface to caller
            log.exception("Control handler failure for action=%s: %s", action, exc)
            return {"ok": False, "error": str(exc)}
        response.setdefault("ok", True)
        return response

    def Ping(self, request, context):  # noqa: N802 - gRPC signature
        del request, context
        return {"ok": True}


def _controller_service_handler(callback: ControlCallback):
    handler = _ControllerRpcHandler(callback)
    return grpc.method_handlers_generic_handler(
        "copper.rpc.ControlService",
        {
            "HandleControl": grpc.unary_unary_rpc_method_handler(
                handler.HandleControl,
                request_deserializer=deserialize_json,
                response_serializer=serialize_json,
            ),
            "Ping": grpc.unary_unary_rpc_method_handler(
                handler.Ping,
                request_deserializer=deserialize_json,
                response_serializer=serialize_json,
            ),
        },
    )


class ControllerRpcServer:
    """gRPC server running inside the controller process to receive commands."""

    def __init__(self, *, endpoint: str, callback: ControlCallback) -> None:
        self._endpoint = endpoint
        self._callback = callback
        self._server: Optional[grpc.Server] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._server is not None:
            return

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        server.add_generic_rpc_handlers((_controller_service_handler(self._callback),))
        address = normalize_endpoint(self._endpoint)
        if not address:
            raise RuntimeError("Controller RPC endpoint is not configured.")
        server.add_insecure_port(address)
        server.start()
        log.info("Controller gRPC server listening at %s", address)

        self._server = server

        def _wait() -> None:
            try:
                server.wait_for_termination()
            except Exception as exc:  # pragma: no cover - background guard
                log.error("Controller gRPC server stopped unexpectedly: %s", exc)

        thread = threading.Thread(target=_wait, name="controller-rpc", daemon=True)
        thread.start()
        self._thread = thread

    def stop(self) -> None:
        server = self._server
        if server is None:
            return
        try:
            server.stop(grace=1).wait()
        except Exception as exc:  # pragma: no cover - best-effort cleanup
            log.warning("Failed to stop Controller gRPC server cleanly: %s", exc)
        self._server = None
        thread = self._thread
        self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=1)
