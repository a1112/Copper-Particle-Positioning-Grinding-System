from __future__ import annotations

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.common.tasks import TaskStatus, TaskType
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
        assert rows[0].task_type == "POLISH_START"
        assert rows[0].device_id == "DEVICE-01"
        assert rows[0].task_params["action"] == "run.start"

    writer.close()


def test_task_queue_writer_logs_control(tmp_path):
    db_path = tmp_path / "control.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    MzPoliShineDB.Base.metadata.create_all(engine)

    writer = TaskQueueWriter(sessionmaker(bind=engine, future=True), engine=engine)
    writer.log_control_task(action="run.start", params={"speed": 120})

    with Session(engine) as session:
        rows = session.query(MzPoliShineDB.TaskTable).all()
        assert len(rows) == 1
        entry = rows[0]
        assert entry.t_task_name == "control:run.start"
        assert entry.t_task_type == int(TaskType.CONTROL)
        assert entry.t_status == int(TaskStatus.PENDING)

    writer.close()
