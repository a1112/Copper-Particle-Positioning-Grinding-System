from __future__ import annotations

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.common.tasks import TaskStatus
from app.controller.http_common import ControllerState, DbStatusSource, TaskQueueWriter
from app.db.models import MzPoliShineDB


def test_production_status_source_build(tmp_path):
    db_path = tmp_path / "status.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    MzPoliShineDB.Base.metadata.create_all(engine)

    with Session(engine) as session:
        record = MzPoliShineDB.StatusTable(
            id=1,
            c_run_status=2,
            c_alarm_status=0,
            c_control_mode=1,
            c_machine_mode=1,
            s_spindle_speed=1500,
            s_feed_speed=220,
            s_point_motion_speed=320,
            s_temperature=Decimal("45.5"),
            s_tool_diameter=Decimal("80.0"),
            p_work_position="100.5, 52.2, -0.7",
        )
        session.add(record)
        session.commit()

    state = ControllerState(label="prod-test")
    source = DbStatusSource(f"sqlite:///{db_path}", engine=engine)

    payload = source.build(state, timestamp=1234.5, cycle=0.0)

    assert payload["state"] == "RUNNING"
    assert payload["run_mode"] == "REMOTE"
    assert payload["spindle_rpm"] == 1500
    assert payload["position"]["x"] == 100.5
    assert payload["metrics"]["s_tool_diameter"] == 80.0
    assert state.run_mode == "REMOTE"

    source.close()


def test_task_queue_writer_enqueue(tmp_path):
    db_path = tmp_path / "queue.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    MzPoliShineDB.Base.metadata.create_all(engine)

    writer = TaskQueueWriter(sessionmaker(bind=engine, future=True), engine=engine)
    writer.enqueue(task_type="POLISH_START", device_id="DEVICE-01", params={"action": "run.start"})

    with Session(engine) as session:
        rows = session.query(MzPoliShineDB.HardwareTaskQueue).all()
        assert len(rows) == 1
        entry = rows[0]
        assert entry.task_name == TaskQueueWriter.DEFAULT_TASK_NAME
        assert entry.task_type == TaskQueueWriter.DEFAULT_TASK_TYPE
        assert entry.device_id == 1
        assert entry.status == int(TaskStatus.PENDING)
        assert entry.task_params["action"] == "POLISH_START"
        assert entry.task_params["params"]["action"] == "run.start"

    writer.close()


def test_task_queue_writer_control_action(tmp_path):
    db_path = tmp_path / "control.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    MzPoliShineDB.Base.metadata.create_all(engine)

    writer = TaskQueueWriter(sessionmaker(bind=engine, future=True), engine=engine)
    writer.enqueue_control_action(
        action="run.start",
        device_id="GRINDER-02",
        params={"speed": 120},
        workpiece_id=5,
        record_id=9,
        task_name_override="控制命令",
        task_type_override=42,
    )

    with Session(engine) as session:
        rows = session.query(MzPoliShineDB.HardwareTaskQueue).all()
        assert len(rows) == 1
        entry = rows[0]
        assert entry.task_name == "控制命令"
        assert entry.task_type == 42
        assert entry.workpiece_id == 5
        assert entry.record_id == 9
        assert entry.device_id == 2
        assert entry.status == int(TaskStatus.PENDING)
        payload = entry.task_params
        assert payload["action"] == "run.start"
        assert payload["params"]["speed"] == 120
        assert payload["action_key"] == "run.start"

    writer.close()
