from __future__ import annotations

import time

from sqlalchemy import delete

from app.common.task_actions import friendly_action_name, friendly_action_type, normalise_action
from app.common.tasks import TaskStatus
from app.db import SessionLocal, init_db
from app.db.models.hardware_task_queue import HardwareTaskQueue
from app.db.models.record_table import RecordTable


def test_ws_tasks_state_emits_changes(client) -> None:
    init_db()
    with SessionLocal() as session:
        session.execute(delete(HardwareTaskQueue))
        session.execute(delete(RecordTable))
        session.commit()

        session.add_all(
            [
                RecordTable(id=1, workpiece_id=1, r_progress_data={"stage": "capture"}),
                RecordTable(id=2, workpiece_id=1, r_progress_data={"stage": "control"}),
            ]
        )
        session.commit()

    with client.websocket_connect("/ws/tasks/state?record_id=1") as ws:
        first = ws.receive_json()
        assert isinstance(first, dict)
        assert first.get("command_record_id") == 1
        assert isinstance(first.get("command_list", []), list)

        with SessionLocal() as session:
            start_type = friendly_action_type("start")
            task = HardwareTaskQueue(
                task_name=friendly_action_name("start"),
                task_type=start_type,
                device_id=1,
                record_id=1,
                task_params={
                    "action": "start",
                    "action_key": normalise_action("start"),
                },
                status=int(TaskStatus.PENDING),
            )
            session.add(task)
            session.commit()

        deadline = time.time() + 6.0
        while time.time() < deadline:
            msg = ws.receive_json()
            commands = msg.get("command_list", [])
            if isinstance(commands, list) and len(commands) >= 1:
                assert commands[0].get("record_id") == 1
                return

        raise AssertionError("did not receive updated task state within timeout")

