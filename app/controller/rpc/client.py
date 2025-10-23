from __future__ import annotations

import logging
import threading
from typing import Any, Iterable, Mapping, Optional, Tuple

import grpc

from app.rpc.common import GRPC_CHANNEL_OPTIONS, deserialize_json, normalize_endpoint, serialize_json

log = logging.getLogger("controller.rpc.client")


class ControllerRpcClient:
    """Client that pushes telemetry snapshots to the API server via gRPC."""

    def __init__(self, *, endpoint: str, timeout: float = 5.0) -> None:
        self._endpoint = endpoint
        self._timeout = timeout
        self._lock = threading.RLock()
        self._channel: Optional[grpc.Channel] = None
        self._push_status: Optional[Any] = None
        self._push_cutting: Optional[Any] = None
        self._push_logs: Optional[Any] = None
        self._ping: Optional[Any] = None

    def _ensure_methods(self) -> Tuple[Any, Any, Any, Any]:
        with self._lock:
            if all((self._push_status, self._push_cutting, self._push_logs, self._ping)):
                return self._push_status, self._push_cutting, self._push_logs, self._ping

            address = normalize_endpoint(self._endpoint)
            if not address:
                raise RuntimeError("Telemetry endpoint is not configured.")

            channel = grpc.insecure_channel(address, options=list(GRPC_CHANNEL_OPTIONS))
            self._channel = channel
            self._push_status = channel.unary_unary(
                "/copper.rpc.TelemetryService/PushStatus",
                request_serializer=serialize_json,
                response_deserializer=deserialize_json,
            )
            self._push_cutting = channel.unary_unary(
                "/copper.rpc.TelemetryService/PushCutting",
                request_serializer=serialize_json,
                response_deserializer=deserialize_json,
            )
            self._push_logs = channel.unary_unary(
                "/copper.rpc.TelemetryService/PushLogs",
                request_serializer=serialize_json,
                response_deserializer=deserialize_json,
            )
            self._ping = channel.unary_unary(
                "/copper.rpc.TelemetryService/Ping",
                request_serializer=serialize_json,
                response_deserializer=deserialize_json,
            )
            log.info("Controller gRPC client connected to %s", address)
            return self._push_status, self._push_cutting, self._push_logs, self._ping

    def _reset(self) -> None:
        with self._lock:
            channel = self._channel
            self._channel = None
            self._push_status = None
            self._push_cutting = None
            self._push_logs = None
            self._ping = None
        if channel is not None:
            try:
                channel.close()
            except Exception:  # pragma: no cover - best-effort cleanup
                pass

    def push_status(self, payload: Mapping[str, Any]) -> bool:
        push_status, _, _, _ = self._ensure_methods()
        try:
            response = push_status(dict(payload or {}), timeout=self._timeout)
        except Exception as exc:
            log.error("push_status failed: %s", exc)
            self._reset()
            raise
        if isinstance(response, dict):
            return bool(response.get("ok", True))
        return bool(response)

    def push_cutting(self, payload: Mapping[str, Any]) -> bool:
        _, push_cutting, _, _ = self._ensure_methods()
        try:
            response = push_cutting(dict(payload or {}), timeout=self._timeout)
        except Exception as exc:
            log.error("push_cutting failed: %s", exc)
            self._reset()
            raise
        if isinstance(response, dict):
            return bool(response.get("ok", True))
        return bool(response)

    def push_logs(self, entries: Iterable[Mapping[str, Any]]) -> bool:
        _, _, push_logs, _ = self._ensure_methods()
        try:
            response = push_logs({"entries": list(entries)}, timeout=self._timeout)
        except Exception as exc:
            log.error("push_logs failed: %s", exc)
            self._reset()
            raise
        if isinstance(response, dict):
            return bool(response.get("ok", True))
        return bool(response)

    def ping(self) -> bool:
        _, _, _, ping_call = self._ensure_methods()
        try:
            result = ping_call(None, timeout=self._timeout)
        except Exception as exc:
            log.debug("gRPC ping failed: %s", exc)
            self._reset()
            return False
        if isinstance(result, dict):
            return bool(result.get("ok", True))
        return bool(result)

    def close(self) -> None:
        self._reset()

