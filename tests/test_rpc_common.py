from __future__ import annotations

import json

import pytest

from app.rpc.common import (
    GRPC_CHANNEL_OPTIONS,
    coerce_mapping,
    coerce_sequence,
    deserialize_json,
    normalize_endpoint,
    serialize_json,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("tcp://127.0.0.1:50051", "127.0.0.1:50051"),
        ("grpc://0.0.0.0:9000", "0.0.0.0:9000"),
        ("http://localhost:8000", "localhost:8000"),
        ("unix:///tmp/socket", "/tmp/socket"),
        ("127.0.0.1:1234", "127.0.0.1:1234"),
        ("", ""),
    ],
)
def test_normalize_endpoint(raw: str, expected: str) -> None:
    assert normalize_endpoint(raw) == expected


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"value": 1},
        {"nested": {"a": 2}},
    ],
)
def test_json_roundtrip(payload: dict[str, object]) -> None:
    data = serialize_json(payload)
    assert isinstance(data, bytes)
    assert deserialize_json(data) == payload


def test_deserialize_empty_payload() -> None:
    assert deserialize_json(b"") is None


class _Custom:
    def __repr__(self) -> str:
        return "<custom>"


def test_serialize_fallback_non_mapping() -> None:
    raw = serialize_json(_Custom())
    # direct json loads to double-check no bytes corruption
    assert json.loads(raw.decode("utf-8")) == {"value": "<custom>"}


def test_coerce_helpers() -> None:
    assert coerce_mapping({"a": 1}) == {"a": 1}
    assert coerce_mapping(None) == {}
    assert coerce_mapping("foo") == {}

    assert coerce_sequence(None) == []
    assert coerce_sequence([1, 2]) == [1, 2]
    assert coerce_sequence((3, 4)) == [3, 4]
    assert coerce_sequence(iter([5])) == [5]
    assert coerce_sequence("abc") == ["abc"]


def test_channel_options_defaults() -> None:
    assert ("grpc.keepalive_time_ms", 30_000) in GRPC_CHANNEL_OPTIONS
