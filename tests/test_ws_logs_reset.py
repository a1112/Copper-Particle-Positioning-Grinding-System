from __future__ import annotations

import time
from typing import Any, Dict

from fastapi.testclient import TestClient


def test_ws_logs_history_on_buffer_reset(client: TestClient) -> None:
    with client.websocket_connect("/ws/logs") as ws:
        first = ws.receive_json()
        assert first.get("type") == "history"
        prev_len = len(first.get("items", []))

        # Produce a log and receive its append
        uniq = f"reset-log-{int(time.time())}"
        resp = client.post("/test/log", params={"msg": uniq})
        assert resp.status_code == 200
        deadline = time.time() + 3.0
        while time.time() < deadline:
            m: Dict[str, Any] = ws.receive_json()
            if m.get("type") == "append" and m.get("item", {}).get("msg") == uniq:
                break

        # Clear buffer -> server should push a new history frame next loop
        resp2 = client.post("/test/log/clear")
        assert resp2.status_code == 200

        deadline2 = time.time() + 5.0
        got_history = False
        while time.time() < deadline2:
            msg = ws.receive_json()
            if msg.get("type") == "history":
                got_history = True
                # After clear, history can be empty or very small
                assert isinstance(msg.get("items"), list)
                break
            # Ignore heartbeat/append while waiting
        assert got_history, "did not receive history after buffer reset"
