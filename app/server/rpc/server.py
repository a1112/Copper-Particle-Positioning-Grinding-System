from __future__ import annotations

import logging
import threading
from concurrent import futures
from typing import Any, Dict, Optional

import grpc

from app.rpc.common import (
    coerce_mapping,
    coerce_sequence,
    deserialize_json,
    normalize_endpoint,
    serialize_json,
)

from .store import RpcDataStore

log = logging.getLogger("app.rpc.server")


class RpcDataReceiver:
    """gRPC handler exposing endpoints for controller components."""

    def __init__(self, store: RpcDataStore) -> None:
        self._store = store

    def push_status(self, payload: Any) -> Dict[str, Any]:
        data = coerce_mapping(payload)
        self._store.update_status(data)
        return {"ok": True}

    def push_cutting(self, payload: Any) -> Dict[str, Any]:
        data = coerce_mapping(payload)
        self._store.update_cutting(data)
        return {"ok": True}

    def push_logs(self, payload: Any) -> Dict[str, Any]:
        entries = payload
        if isinstance(payload, dict) and "entries" in payload:
            entries = payload.get("entries")
        if isinstance(entries, dict):
            self._store.append_log(dict(entries))
            return {"ok": True}

        try:
            iterator = coerce_sequence(entries)
        except Exception:  # pragma: no cover - defensive fallback
            self._store.append_log({"message": str(entries)})
            return {"ok": True}

        mapped = []
        for item in iterator:
            if isinstance(item, dict):
                mapped.append(dict(item))
            else:
                mapped.append({"message": str(item)})

        if not mapped:
            return {"ok": True}
        if len(mapped) == 1:
            self._store.append_log(mapped[0])
        else:
            self._store.extend_logs(mapped)
        return {"ok": True}

    def ping(self) -> Dict[str, Any]:
        return {"ok": True}


class _TelemetryService:
    def __init__(self, receiver: RpcDataReceiver) -> None:
        self._receiver = receiver

    def PushStatus(self, request, context):  # noqa: N802 - gRPC signature
        _ = context
        return self._receiver.push_status(request)

    def PushCutting(self, request, context):  # noqa: N802 - gRPC signature
        _ = context
        return self._receiver.push_cutting(request)

    def PushLogs(self, request, context):  # noqa: N802 - gRPC signature
        _ = context
        return self._receiver.push_logs(request)

    def Ping(self, request, context):  # noqa: N802 - gRPC signature
        del request, context
        return self._receiver.ping()


def _telemetry_service_handler(receiver: RpcDataReceiver):
    service = _TelemetryService(receiver)
    return grpc.method_handlers_generic_handler(
        "copper.rpc.TelemetryService",
        {
            "PushStatus": grpc.unary_unary_rpc_method_handler(
                service.PushStatus,
                request_deserializer=deserialize_json,
                response_serializer=serialize_json,
            ),
            "PushCutting": grpc.unary_unary_rpc_method_handler(
                service.PushCutting,
                request_deserializer=deserialize_json,
                response_serializer=serialize_json,
            ),
            "PushLogs": grpc.unary_unary_rpc_method_handler(
                service.PushLogs,
                request_deserializer=deserialize_json,
                response_serializer=serialize_json,
            ),
            "Ping": grpc.unary_unary_rpc_method_handler(
                service.Ping,
                request_deserializer=deserialize_json,
                response_serializer=serialize_json,
            ),
        },
    )


class RpcServerRunner:
    """Background gRPC server bound to an endpoint."""

    def __init__(self, *, endpoint: str, store: RpcDataStore) -> None:
        self._endpoint = endpoint
        self._store = store
        self._server: Optional[grpc.Server] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._server is not None:
            return
        receiver = RpcDataReceiver(self._store)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
        server.add_generic_rpc_handlers((_telemetry_service_handler(receiver),))

        address = normalize_endpoint(self._endpoint)
        if not address:
            raise RuntimeError("RPC endpoint is not configured.")
        server.add_insecure_port(address)
        server.start()
        log.info("gRPC telemetry server listening at %s", address)

        self._server = server

        def _wait() -> None:
            try:
                server.wait_for_termination()
            except Exception as exc:  # pragma: no cover - background guard
                log.error("gRPC telemetry server stopped unexpectedly: %s", exc)

        thread = threading.Thread(target=_wait, name="rpc-server", daemon=True)
        thread.start()
        self._thread = thread

    def stop(self) -> None:
        server = self._server
        if server is None:
            return
        try:
            server.stop(grace=1).wait()
        except Exception as exc:  # pragma: no cover - best-effort shutdown
            log.warning("Failed to stop gRPC server cleanly: %s", exc)
        self._server = None
        thread = self._thread
        self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=1)
