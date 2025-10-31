from __future__ import annotations

import importlib
import os

import pytest
from sqlalchemy import delete, func, select

from app.server.api.ws.code_bus import bus
from app.server.httpbridge.routes import set_store
from app.server.httpbridge.store import HttpDataStore
from app.db import SessionLocal, init_db
from app.db.models.param_settings import ParamSettings
from app.db.models.hardware_task_queue import HardwareTaskQueue
from app.db.models.record_table import RecordTable
from app.db.models.workpiece_table import WorkpieceTable
from app.db.models.tool_record import ToolRecord
from app.common.task_actions import friendly_action_name, friendly_action_type, normalise_action


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
    assert "categories" in data
    categories = data["categories"]
    assert "general" in categories
    assert "process" in categories
    assert "algorithm" in categories
    algorithm = categories["algorithm"]
    assert "pre_process" in algorithm
    assert "defect" in algorithm
    assert "tools" in data and isinstance(data["tools"], list)


def test_settings_parameters_roundtrip(client):
    init_db()
    with SessionLocal() as session:
        session.execute(delete(ParamSettings))
        session.execute(delete(ToolRecord))
        session.commit()

    r = client.get("/settings/parameters")
    assert r.status_code == 200
    payload = r.json()
    categories = payload.get("categories", {})
    assert set(categories.keys()) == {"general", "process", "algorithm"}
    assert "placeholders" in categories["general"]
    assert "placeholders" in categories["process"]
    assert "pre_process" in categories["algorithm"]

    new_algorithm = {
        "pre_process": {
            "plane_distance": {
                "enabled": True,
                "sample_distance": 4.5,
                "angle_threshold": 1.1,
                "distance_threshold": 7.0,
                "plane_distance_min": 1.5,
                "plane_distance_max": 50.0,
            }
        },
        "defect": {"normal_threshold": 0.25},
    }
    r = client.put("/settings/parameters/algorithm", json=new_algorithm)
    assert r.status_code == 200
    updated = r.json().get("payload", {})
    assert updated["pre_process"]["plane_distance"]["enabled"] is True
    assert updated["defect"]["normal_threshold"] == 0.25

    r = client.get("/settings/parameters/algorithm")
    assert r.status_code == 200
    fetched = r.json().get("payload", {})
    assert fetched["pre_process"]["plane_distance"]["distance_threshold"] == 7.0

    r = client.get("/settings/parameters/algorithm/export")
    assert r.status_code == 200
    exported = r.json().get("content", "")
    assert "plane_distance_max: 50.0" in exported

    yaml_text = "\n".join(
        [
            "pre_process:",
            "  plane_distance:",
            "    enabled: false",
            "    distance_threshold: 5.5",
        ]
    )
    r = client.post("/settings/parameters/algorithm/import", json={"content": yaml_text})
    assert r.status_code == 200
    imported = r.json().get("payload", {})
    assert imported["pre_process"]["plane_distance"]["enabled"] is False
    assert imported["pre_process"]["plane_distance"]["distance_threshold"] == 5.5

    r = client.post("/settings/parameters/algorithm/import", json={"content": 123})
    assert r.status_code == 400

    r = client.get("/settings/parameters/unknown")
    assert r.status_code == 404


def test_settings_tools_crud(client):
    init_db()
    with SessionLocal() as session:
        session.execute(delete(ToolRecord))
        session.commit()

    r = client.get("/settings/tools")
    assert r.status_code == 200
    assert isinstance(r.json().get("tools"), list)

    payload = {
        "tools": [
            {
                "model": "D40",
                "diameter_mm": 40.0,
                "length_mm": 120.0,
                "usage_minutes": 0,
                "service_life_minutes": 600,
                "status": 0,
            }
        ]
    }
    r = client.put("/settings/tools", json=payload)
    assert r.status_code == 200
    tools = r.json().get("tools", [])
    assert len(tools) == 1
    tool_id = tools[0]["id"]
    assert tools[0]["model"] == "D40"

    update_payload = {
        "tools": [
            {
                "id": tool_id,
                "model": "D40",
                "diameter_mm": 40.0,
                "length_mm": 120.0,
                "usage_minutes": 30,
                "service_life_minutes": 600,
                "status": 1,
            },
            {
                "model": "D20",
                "diameter_mm": 20.0,
                "length_mm": 80.0,
                "usage_minutes": 0,
                "service_life_minutes": 400,
                "status": 0,
            },
        ]
    }
    r = client.put("/settings/tools", json=update_payload)
    assert r.status_code == 200
    updated_tools = {item["model"]: item for item in r.json().get("tools", [])}
    assert updated_tools["D40"]["usage_minutes"] == 30
    assert updated_tools["D40"]["status"] == 1
    assert "D20" in updated_tools

    r = client.put("/settings/tools", json={"tools": "invalid"})
    assert r.status_code == 400


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


def test_capture_endpoint_creates_record(client):
    init_db()
    with SessionLocal() as session:
        session.execute(delete(HardwareTaskQueue))
        session.execute(delete(RecordTable))
        session.execute(delete(WorkpieceTable))
        session.commit()

    r = client.post("/capture", json={"note": "pytest"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    record_id = data.get("record_id")
    assert isinstance(record_id, int) and record_id > 0
    assert data.get("record", {}).get("id") == record_id

    with SessionLocal() as session:
        queue_count = session.execute(
            select(func.count()).select_from(HardwareTaskQueue)
        ).scalar_one()
        assert queue_count == 0
        record = session.get(RecordTable, record_id)
        assert record is not None


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

        start_type = friendly_action_type("start")
        stop_type = friendly_action_type("stop")
        task1 = HardwareTaskQueue(
            id=1001,
            task_name=friendly_action_name("start"),
            task_type=start_type,
            device_id=1,
            record_id=record1.id,
            task_params={
                "action": "start",
                "action_key": normalise_action("start"),
            },
            status=0,
        )
        task2 = HardwareTaskQueue(
            id=1002,
            task_name=friendly_action_name("stop"),
            task_type=stop_type,
            device_id=1,
            record_id=record2.id,
            task_params={
                "action": "stop",
                "action_key": normalise_action("stop"),
            },
            status=0,
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

