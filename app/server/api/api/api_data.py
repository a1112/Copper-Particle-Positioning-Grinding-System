from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import delete, desc, func, select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.db.models.MzPoliShineDB import AlarmTable, HardwareTaskQueue, RecordTable, WorkpieceTable
from app.server.api.api_core import data_router as router
from app.common.tasks import TaskStatus, TaskType
from app import config

SAVE_DATA_DIR = Path(config.PROJECT_ROOT) / 'SaveData'
CRITICAL_ALARM_LEVEL = 3


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class WorkpieceCreatePayload(BaseModel):
    workpiece_code: Optional[str] = Field(default=None, alias='code')
    workpiece_type: Optional[str] = Field(default=None, alias='type')
    material: Optional[str] = None
    dimensions: Optional[str] = None
    surface_requirement: Optional[str] = None
    roughness_required: Optional[float] = None


class CaptureRequestPayload(BaseModel):
    workpiece_id: Optional[int] = None
    note: Optional[str] = None


class ExecuteRequestPayload(BaseModel):
    record_id: Optional[int] = None
    workpiece_id: Optional[int] = None


class AlarmResetPayload(BaseModel):
    handler: Optional[str] = None


class AlarmTestPayload(BaseModel):
    record_id: Optional[int] = None
    alarm_type: Optional[str] = Field(default=None, alias='type')
    alarm_code: Optional[str] = Field(default=None, alias='code')
    alarm_message: Optional[str] = Field(default=None, alias='message')
    alarm_level: int = Field(default=3, ge=0, le=10)

def _serialize_workpiece(row: WorkpieceTable) -> Dict[str, Any]:
    return {
        'id': row.id,
        'code': row.w_workpiece_id,
        'type': row.w_workpiece_type,
        'material': row.w_material,
        'dimensions': row.w_dimensions,
        'surface_requirement': row.w_surface_requirement,
        'roughness_required': float(row.w_roughness_required) if row.w_roughness_required is not None else None,
        'status': row.w_status,
        'created_time': row.created_time.isoformat() if row.created_time else None,
    }


def _ensure_default_workpiece(session: Session) -> WorkpieceTable:
    row = session.execute(select(WorkpieceTable).order_by(desc(WorkpieceTable.id))).scalars().first()
    if row:
        return row
    record = WorkpieceTable(
        w_workpiece_id='WP-DEMO-0001',
        w_workpiece_type='DEMO',
        w_material='Copper',
        w_dimensions='100x100x10',
        w_surface_requirement='Ra <= 0.2',
        w_status=0,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def _get_workpiece(session: Session, workpiece_id: Optional[int]) -> WorkpieceTable:
    if workpiece_id:
        row = session.get(WorkpieceTable, workpiece_id)
        if row is None:
            raise HTTPException(status_code=404, detail='Workpiece not found')
        return row
    return _ensure_default_workpiece(session)


def _serialize_task(row: HardwareTaskQueue) -> Dict[str, Any]:
    payload = row.task_params or {}
    if not isinstance(payload, dict):
        payload = {"value": payload}
    params_field = payload.get("params")
    params = params_field if isinstance(params_field, dict) else params_field
    status_detail = row.status_params if isinstance(row.status_params, dict) else {}
    return {
        'id': row.id,
        'name': row.task_name,
        'type': row.task_type,
        'status': row.status,
        'priority': row.priority,
        'workpiece_id': row.workpiece_id,
        'record_id': row.record_id,
        'device_id': row.device_id,
        'payload': payload,
        'command': payload.get('action'),
        'command_key': payload.get('action_key'),
        'command_name': payload.get('action_name'),
        'command_params': params,
        'queued_at': payload.get('queued_at'),
        'remark': payload.get('remark') or payload.get('note'),
        'status_detail': status_detail,
        'created_time': row.created_time.isoformat() if row.created_time else None,
        'updated_time': row.updated_time.isoformat() if row.updated_time else None,
    }


def _serialize_alarm(row: AlarmTable) -> Dict[str, Any]:
    return {
        'id': row.id,
        'record_id': row.record_id,
        'type': row.alarm_type,
        'code': row.alarm_code,
        'message': row.alarm_message,
        'level': row.alarm_level,
        'handled_status': row.handled_status,
        'alarm_time': row.alarm_time.isoformat() if row.alarm_time else None,
        'handled_time': row.handled_time.isoformat() if row.handled_time else None,
        'handler': row.handler,
    }


@router.get('/data/workpieces/current')
def get_current_workpiece(session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    row = _ensure_default_workpiece(session)
    return {'workpiece': _serialize_workpiece(row)}


@router.post('/data/workpieces')
def create_workpiece(payload: WorkpieceCreatePayload, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    code = (payload.workpiece_code or '').strip()
    if not code:
        latest = session.execute(select(WorkpieceTable).order_by(desc(WorkpieceTable.id))).scalars().first()
        next_id = (latest.id + 1) if latest else 1
        code = f'WP-{next_id:05d}'
    record = WorkpieceTable(
        w_workpiece_id=code,
        w_workpiece_type=payload.workpiece_type,
        w_material=payload.material,
        w_dimensions=payload.dimensions,
        w_surface_requirement=payload.surface_requirement,
        w_roughness_required=payload.roughness_required,
        w_status=0,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return {'ok': True, 'workpiece': _serialize_workpiece(record)}


@router.get('/data/workpieces')
def list_workpieces(
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    rows = (
        session.execute(
            select(WorkpieceTable)
            .order_by(desc(WorkpieceTable.id))
            .limit(limit)
        )
        .scalars()
        .all()
    )
    total = session.execute(select(func.count()).select_from(WorkpieceTable)).scalar_one()
    return {'workpieces': [_serialize_workpiece(row) for row in rows], 'total': total}


@router.delete('/data/workpieces/{workpiece_id}')
def delete_workpiece(workpiece_id: int, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    row = session.get(WorkpieceTable, workpiece_id)
    if row is None:
        raise HTTPException(status_code=404, detail='Workpiece not found')
    session.delete(row)
    session.commit()
    return {'ok': True, 'workpiece_id': workpiece_id}


def _ensure_save_dir(record_id: int) -> Path:
    SAVE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    folder = SAVE_DATA_DIR / f"record_{record_id:06d}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@router.post('/data/records/capture')
def create_capture_record(payload: CaptureRequestPayload, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    workpiece = _get_workpiece(session, payload.workpiece_id)
    record = RecordTable(
        workpiece_id=workpiece.id,
        r_progress_data={'stage': 'capture_pending'},
    )
    session.add(record)
    session.flush()

    folder = _ensure_save_dir(record.id)
    task = HardwareTaskQueue(
        task_name=f'capture-{record.id}',
        task_type=int(TaskType.CAPTURE),
        workpiece_id=workpiece.id,
        record_id=record.id,
        status=int(TaskStatus.PENDING),
        task_params={'folder': str(folder), 'note': payload.note or '', 'queued_at': datetime.utcnow().timestamp()},
        status_params={'phase': 'queued'},
        device_id=1,
    )
    session.add(task)
    session.commit()
    session.refresh(record)
    session.refresh(task)
    return {
        'ok': True,
        'record': {'id': record.id, 'workpiece_id': record.workpiece_id},
        'task': _serialize_task(task),
    }


@router.post('/data/tasks/execute')
def enqueue_execute_task(payload: ExecuteRequestPayload, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    record = None
    if payload.record_id:
        record = session.get(RecordTable, payload.record_id)
        if record is None:
            raise HTTPException(status_code=404, detail='Record not found')
    if record is None:
        workpiece = _get_workpiece(session, payload.workpiece_id)
        record = session.execute(
            select(RecordTable)
            .where(RecordTable.workpiece_id == workpiece.id)
            .order_by(desc(RecordTable.id))
        ).scalars().first()
        if record is None:
            raise HTTPException(status_code=400, detail='No capture record available for this workpiece')
    task = HardwareTaskQueue(
        task_name=f'execute-{record.id}',
        task_type=int(TaskType.EXECUTE),
        workpiece_id=record.workpiece_id,
        record_id=record.id,
        status=int(TaskStatus.PENDING),
        task_params={'record_id': record.id, 'queued_at': datetime.utcnow().timestamp()},
        status_params={'phase': 'queued'},
        device_id=1,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return {'ok': True, 'task': _serialize_task(task)}


@router.get('/data/records/{record_id}/alarms')
def list_record_alarms(record_id: int, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    record = session.get(RecordTable, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail='Record not found')
    return _alarm_summary_for_record(session, record_id)


@router.post('/data/records/{record_id}/alarms/reset')
def reset_record_alarms(record_id: int, payload: AlarmResetPayload, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    record = session.get(RecordTable, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail='Record not found')
    rows: List[AlarmTable] = (
        session.execute(
            select(AlarmTable)
            .where(AlarmTable.record_id == record_id)
            .where(AlarmTable.handled_status < 2)
        )
        .scalars()
        .all()
    )
    if not rows:
        summary = _alarm_summary_for_record(session, record_id)
        return {'ok': True, 'updated': 0, 'alarm_summary': summary}

    now = datetime.utcnow()
    handler = (payload.handler or '').strip() or None
    updated = 0
    for item in rows:
        item.handled_status = 2
        item.handled_time = now
        if handler:
            item.handler = handler
        updated += 1
    session.commit()
    summary = _alarm_summary_for_record(session, record_id)
    return {'ok': True, 'updated': updated, 'alarm_summary': summary}


@router.post('/diagnostics/alarms/test')
def create_test_alarm(payload: AlarmTestPayload, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    record: Optional[RecordTable] = None
    if payload.record_id:
        record = session.get(RecordTable, payload.record_id)
        if record is None:
            raise HTTPException(status_code=404, detail='Record not found')
    if record is None:
        record = session.execute(select(RecordTable).order_by(desc(RecordTable.id))).scalars().first()
        if record is None:
            workpiece = _ensure_default_workpiece(session)
            record = RecordTable(
                workpiece_id=workpiece.id,
                r_progress_data={'stage': 'test_alarm'},
            )
            session.add(record)
            session.flush()
    now = datetime.utcnow()
    level = int(payload.alarm_level or 0)
    alarm = AlarmTable(
        record_id=record.id,
        alarm_type=(payload.alarm_type or 'TEST'),
        alarm_code=(payload.alarm_code or f'TEST-{now.strftime("%H%M%S")}'),
        alarm_message=(payload.alarm_message or 'Test alarm generated from diagnostics button'),
        alarm_level=level,
        handled_status=0,
        alarm_time=now,
    )
    session.add(alarm)
    session.commit()
    session.refresh(alarm)
    summary = _alarm_summary_for_record(session, record.id)
    return {'ok': True, 'alarm': _serialize_alarm(alarm), 'alarm_summary': summary}

def _latest_task(session: Session, task_type: TaskType) -> Optional[HardwareTaskQueue]:
    return (
        session.execute(
            select(HardwareTaskQueue)
            .where(HardwareTaskQueue.task_type == int(task_type))
            .order_by(desc(HardwareTaskQueue.id))
        )
        .scalars()
        .first()
    )


def _alarm_summary_for_record(session: Session, record_id: Optional[int]) -> Dict[str, Any]:
    if not record_id:
        return {'alarms': [], 'max_level': 0, 'requires_reset': False}
    rows: List[AlarmTable] = (
        session.execute(
            select(AlarmTable)
            .where(AlarmTable.record_id == record_id)
            .order_by(desc(AlarmTable.alarm_time))
        )
        .scalars()
        .all()
    )
    max_level = 0
    requires_reset = False
    alarms: List[Dict[str, Any]] = []
    for row in rows:
        level = int(row.alarm_level or 0)
        max_level = max(max_level, level)
        if level >= CRITICAL_ALARM_LEVEL and int(row.handled_status or 0) < 2:
            requires_reset = True
        alarms.append(_serialize_alarm(row))
    return {'alarms': alarms, 'max_level': max_level, 'requires_reset': requires_reset}


@router.get('/data/tasks/state')
def task_state_summary(
    record_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    workpiece = _ensure_default_workpiece(session)
    record = session.execute(select(RecordTable).order_by(desc(RecordTable.id))).scalars().first()

    latest_capture = _latest_task(session, TaskType.CAPTURE)
    latest_execute = _latest_task(session, TaskType.EXECUTE)
    latest_control = _latest_task(session, TaskType.CONTROL)

    capture_active = latest_capture and latest_capture.status in (int(TaskStatus.PENDING), int(TaskStatus.RUNNING))
    execute_active = latest_execute and latest_execute.status in (int(TaskStatus.PENDING), int(TaskStatus.RUNNING))
    capture_ready = bool(latest_capture and latest_capture.status == int(TaskStatus.COMPLETED))
    execute_ready = capture_ready and not execute_active

    control_stmt = (
        select(HardwareTaskQueue)
        .where(HardwareTaskQueue.task_type == int(TaskType.CONTROL))
        .order_by(desc(HardwareTaskQueue.id))
    )
    record_filter_id: Optional[int] = None
    if record_id is not None and record_id > 0:
        record_filter_id = record_id
    elif record is not None:
        record_filter_id = record.id
    if record_filter_id is not None:
        control_stmt = control_stmt.where(HardwareTaskQueue.record_id == record_filter_id)
    control_rows = session.execute(control_stmt).scalars().all()
    control_commands = [_serialize_task(row) for row in control_rows]

    gcode_payload: Any = None
    if record and record.r_algorithm_data:
        gcode_payload = record.r_algorithm_data

    alarm_summary = _alarm_summary_for_record(session, record.id if record else None)

    return {
        'workpiece': _serialize_workpiece(workpiece) if workpiece else None,
        'latest_record': record.id if record else None,
        'capture': _serialize_task(latest_capture) if latest_capture else None,
        'execute': _serialize_task(latest_execute) if latest_execute else None,
        'control': _serialize_task(latest_control) if latest_control else None,
        'command_record_id': record_filter_id,
        'command_list': control_commands,
        'ready': {
            'capture': not bool(capture_active),
            'execute': execute_ready,
            'record_id': record.id if record else None,
        },
        'gcode': gcode_payload,
        'alarm_max_level': alarm_summary['max_level'],
        'alarm_requires_reset': alarm_summary['requires_reset'],
    }


@router.delete('/data/tasks/control/{task_id}')
def delete_control_task(task_id: int, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    row = session.get(HardwareTaskQueue, task_id)
    if row is None or row.task_type != int(TaskType.CONTROL):
        raise HTTPException(status_code=404, detail='Control task not found')
    session.delete(row)
    session.commit()
    return {'ok': True, 'task_id': task_id}


@router.delete('/data/tasks/control')
def clear_control_tasks(session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    stmt = delete(HardwareTaskQueue).where(HardwareTaskQueue.task_type == int(TaskType.CONTROL))
    result = session.execute(stmt)
    session.commit()
    return {'ok': True, 'deleted': result.rowcount or 0}
