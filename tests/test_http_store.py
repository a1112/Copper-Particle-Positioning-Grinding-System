from __future__ import annotations

from app.server.httpbridge.store import HttpDataStore


def test_http_data_store_roundtrip() -> None:
    store = HttpDataStore(log_capacity=2)
    payload = {"state": "RUNNING"}
    store.update_status(payload)
    assert store.get_status() == payload

    cutting = {"torque": 1.2}
    store.update_cutting(cutting)
    assert store.get_cutting() == cutting

    store.append_log({"message": "one"})
    store.extend_logs([{"message": "two"}, {"message": "three"}])
    logs = list(store.get_logs())
    assert logs[-1]["message"] == "three"
    assert len(logs) <= 2  # bounded by capacity

