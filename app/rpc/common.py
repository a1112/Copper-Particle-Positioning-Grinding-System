from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Mapping, Sequence


def normalize_endpoint(endpoint: str) -> str:
    """Return a gRPC-friendly endpoint string (host:port)."""
    if not endpoint:
        return endpoint
    value = endpoint.strip()
    lowered = value.lower()
    for prefix in ("tcp://", "grpc://", "http://", "https://"):
        if lowered.startswith(prefix):
            return value[len(prefix) :]
    if lowered.startswith("unix://"):
        return value[len("unix://") :]
    return value


def serialize_json(payload: Any) -> bytes:
    """Serialize arbitrary JSON-compatible data for gRPC transport."""

    def _default(obj: Any) -> Any:
        try:
            return dict(obj)  # type: ignore[arg-type]
        except Exception:
            return repr(obj)

    try:
        return json.dumps(payload, default=_default, separators=(",", ":")).encode("utf-8")
    except TypeError:
        fallback = _safe_mapping(payload)
        return json.dumps(fallback, default=_default, separators=(",", ":")).encode("utf-8")


def deserialize_json(data: bytes) -> Any:
    """Deserialize JSON payloads coming from gRPC handlers."""
    if not data:
        return None
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _safe_mapping(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, Mapping):
        return dict(payload)
    return {"value": repr(payload)}


def coerce_mapping(payload: Any) -> Dict[str, Any]:
    """Convert arbitrary payloads to a dict, defaulting to an empty mapping."""
    if payload is None:
        return {}
    if isinstance(payload, Mapping):
        return dict(payload)
    return {}


def coerce_sequence(payload: Any) -> List[Any]:
    """Convert payloads to a list when possible, otherwise wrap in a single-item list."""
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        return list(payload)
    if isinstance(payload, Iterable) and not isinstance(payload, (str, bytes, bytearray)):
        return list(payload)
    return [payload]


GRPC_CHANNEL_OPTIONS = (
    ("grpc.keepalive_time_ms", 30_000),
    ("grpc.keepalive_timeout_ms", 10_000),
    ("grpc.http2.max_pings_without_data", 0),
    ("grpc.keepalive_permit_without_calls", 1),
)


__all__ = [
    "GRPC_CHANNEL_OPTIONS",
    "coerce_mapping",
    "coerce_sequence",
    "deserialize_json",
    "normalize_endpoint",
    "serialize_json",
]
