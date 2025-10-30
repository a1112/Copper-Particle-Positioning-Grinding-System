from __future__ import annotations

import importlib
import os

import pytest
from sqlalchemy import delete

from app.server.api.ws.code_bus import bus
from app.server.httpbridge.routes import set_store
from app.server.httpbridge.store import HttpDataStore
from app.db import SessionLocal, init_db
from app.db.models.hardware_task_queue import HardwareTaskQueue
from app.db.models.record_table import RecordTable
from app.db.models.workpiece_table import WorkpieceTable
from app.common.tasks import TaskType


def test_root_docs_hint(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "/docs" in r.json().get("/docs", "") or "/docs" in r.text


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_image_png(client):
    r = client.get("/image.png")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "image/png"
    assert len(r.content) > 0


def test_list_test_images(client):
    r = client.get("/test/images")
    assert r.status_code == 200
    data = r.json()
    assert "files" in data
    assert isinstance(data["files"], list)
    # Should include at least one known example asset
    assert any(
        name.endswith("1_IMG_Texture_8Bit.png") or name.endswith("2_IMG_Texture_8Bit.png")
        for name in data["files"]
    )


@pytest.mark.skipif(
    importlib.util.find_spec("cv2") is None, reason="cv2 not installed in test environment"
)
def test_load_default_image(client):
    r = client.post("/test/load_default")
    # When images exist, endpoint returns ok True
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        assert r.json().get("ok") is True


def test_motion_endpoints_noop_ok(client):
    # Even without a concrete motion controller, endpoints should return ok
    r1 = client.post("/motion/home")
    r2 = client.post("/motion/set_work_origin")
    assert r1.status_code == 200 and r1.json().get("ok") is True
    assert r2.status_code == 200 and r2.json().get("ok") is True


def test_config_settings_bundle(client):
    r = client.get("/config/settings")
    assert r.status_code == 200
    data = r.json()
    assert "sources" in data and data["sources"]["job"].endswith("job_default.yaml")
    assert any(section["name"] == "scan" for section in data.get("job_sections", []))
    assert isinstance(data.get("tool_table"), list) and len(data["tool_table"]) >= 1

    scan_section = next(section for section in data.get("job_sections", []) if section["name"] == "scan")
    scan_mode = next(item for item in scan_section.get("items", []) if item["key"] == "mode")
    assert isinstance(scan_mode.get("description"), str) and len(scan_mode["description"]) > 0

def test_tool_list_endpoint(client):
    r = client.get("/toolList")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        sample = data[0]
        assert isinstance(sample, dict)
        assert "model" in sample
        assert "diameter_mm" in sample


def test_bridge_controller_program(client):
    store = HttpDataStore()
    set_store(store)

    payload = {
        "program": ["%", "M30"],
        "program_state": {"state": "IDLE", "current": 1},
    }
    r = client.post("/bridge/controller", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert data.get("lines") == 2
    assert store.get_program() == payload["program"]
    assert store.get_program_state().get("state") == "IDLE"
    assert bus.latest_program() == payload["program"]

    # Clear program to avoid leaking state into other tests
    client.post("/bridge/controller", json={"program": []})


def test_task_state_command_filter_by_record(client):
    init_db()
    with SessionLocal() as session:
        session.execute(delete(HardwareTaskQueue))
        session.execute(delete(RecordTable))
        session.execute(delete(WorkpieceTable))
        session.commit()

        workpiece = WorkpieceTable(
            id=1,
            w_workpiece_id="WP-FILTER",
            w_workpiece_type="TEST",
            w_material="Copper",
            w_dimensions="10x10x1",
            w_surface_requirement="Test",
        )
        session.add(workpiece)
        session.flush()

        record1 = RecordTable(id=1, workpiece_id=workpiece.id)
        record2 = RecordTable(id=2, workpiece_id=workpiece.id)
        session.add_all([record1, record2])
        session.flush()

        task1 = HardwareTaskQueue(
            id=1001,
            task_name="start",
            task_type=int(TaskType.CONTROL),
            device_id=1,
            record_id=record1.id,
            task_params={"action": "start"},
        )
        task2 = HardwareTaskQueue(
            id=1002,
            task_name="stop",
            task_type=int(TaskType.CONTROL),
            device_id=1,
            record_id=record2.id,
            task_params={"action": "stop"},
        )
        session.add_all([task1, task2])
        session.commit()

    r = client.get("/data/tasks/state?record_id=1")
    assert r.status_code == 200
    data = r.json()
    commands = data.get("command_list", [])
    assert len(commands) == 1
    assert commands[0]["record_id"] == 1
    assert data.get("command_record_id") == 1
