from __future__ import annotations

import asyncio
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def ws_client(app_and_ws) -> TestClient:
    app, ws_status = app_and_ws

    async def _dummy_status() -> Dict[str, Any]:
        return {
            "state": "IDLE",
            "position": {"x": 0, "y": 0, "z": 0, "theta": 0},
            "spindle_rpm": 0,
            "spindle_torque": 0.0,
            "seriesA": 0,
            "seriesB": 0,
        }

    # Inject the status function expected by ws handler
    setattr(ws_status, "status_fn", _dummy_status)

    return TestClient(app)


def test_ws_status_stream(ws_client: TestClient):
    with ws_client.websocket_connect("/ws/status") as ws:
        msg = ws.receive_json()
        # Basic shape assertions
        assert isinstance(msg, dict)
        assert msg.get("state") == "IDLE"
        assert "position" in msg and isinstance(msg["position"], dict)

