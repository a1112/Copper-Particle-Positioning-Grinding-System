from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Mapping, Optional, Tuple

import grpc

from app.rpc.common import GRPC_CHANNEL_OPTIONS, deserialize_json, normalize_endpoint, serialize_json

log = logging.getLogger("app.rpc.client")


class RpcControlClient:
    """Lazy gRPC client used to dispatch control commands to the controller."""

    def __init__(self, *, endpoint: str, timeout: float = 5.0) -> None:
        self._endpoint = endpoint
        self._timeout = timeout
        self._lock = threading.RLock()
        self._channel: Optional[grpc.Channel] = None
        self._handle_control: Optional[Any] = None
        self._ping: Optional[Any] = None

    def _ensure_methods(self) -> Tuple[Any, Any]:
        with self._lock:
            if self._handle_control is not None and self._ping is not None:
                return self._handle_control, self._ping

            address = normalize_endpoint(self._endpoint)
            if not address:
                raise RuntimeError("Control endpoint is not configured.")
            channel = grpc.insecure_channel(address, options=list(GRPC_CHANNEL_OPTIONS))
            self._channel = channel
            self._handle_control = channel.unary_unary(
                "/copper.rpc.ControlService/HandleControl",
                request_serializer=serialize_json,
                response_deserializer=deserialize_json,
            )
            self._ping = channel.unary_unary(
                "/copper.rpc.ControlService/Ping",
                request_serializer=serialize_json,
                response_deserializer=deserialize_json,
            )
            log.info("gRPC control client connected to %s", address)
            return self._handle_control, self._ping

    def _reset(self) -> None:
        with self._lock:
            channel = self._channel
            self._channel = None
            self._handle_control = None
            self._ping = None
        if channel is not None:
            try:
                channel.close()
            except Exception:  # pragma: no cover - best-effort cleanup
                pass

    def handle_control(self, action: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        payload = {"action": action, "params": dict(params or {})}
        handle_control, _ = self._ensure_methods()
        try:
            response = handle_control(payload, timeout=self._timeout)
        except Exception as exc:
            log.error("gRPC control call failed: %s", exc)
            self._reset()
            raise
        if not isinstance(response, dict):
            return {"ok": bool(response), "raw": response}
        response.setdefault("ok", True)
        return response

    def ping(self) -> bool:
        _, ping_call = self._ensure_methods()
        try:
            result = ping_call(None, timeout=self._timeout)
            if isinstance(result, dict):
                return bool(result.get("ok", True))
            return bool(result)
        except Exception as exc:
            log.debug("gRPC ping failed: %s", exc)
            self._reset()
            return False

    def close(self) -> None:
        self._reset()
