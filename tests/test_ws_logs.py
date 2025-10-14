from __future__ import annotations

import json
import time
from typing import Any, Dict

from fastapi.testclient import TestClient


def test_ws_logs_history_and_append(client: TestClient) -> None:
    # Connect to logs websocket
    with client.websocket_connect("/ws/logs") as ws:
        # First message must be a history snapshot
        first = ws.receive_json()
        assert isinstance(first, dict)
        assert first.get("type") == "history"
        assert isinstance(first.get("items"), list)

        # Trigger a test log via HTTP and expect an append frame
        uniq = f"pytest-log-{int(time.time())}"
        resp = client.post("/test/log", params={"msg": uniq})
        assert resp.status_code == 200

        deadline = time.time() + 5.0
        seen = False
        while time.time() < deadline:
            msg: Dict[str, Any] = ws.receive_json()
            if msg.get("type") != "append":
                continue
            item = msg.get("item", {})
            # Ignore heartbeat frames and unrelated logs
            if item.get("name") == "app" and item.get("msg") == "heartbeat":
                continue
            if item.get("msg") == uniq:
                seen = True
                # Basic shape
                assert item.get("level") in {"INFO", "WARN", "ERROR", "DEBUG"}
                assert isinstance(item.get("ts"), (int, float))
                                # extra field: human time string\n                assert isinstance(item.get('time'), str) and ':' in item.get('time')\n                break\n        assert seen, "did not receive append for test log within timeout"

