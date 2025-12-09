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
from app.common.tasks import TaskStatus
from app.common.task_actions import (
    ACTION_META,
    DEFAULT_TASK_TYPE as TASK_DEFAULT_TYPE,
    friendly_action_type,
)
from app.server.api.services.settings_store import SettingsStore
from app import config
from app.common import save_data
from app.controller.http_common import program

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


class AlarmResetPayload(BaseModel):
    handler: Optional[str] = None


class AlarmTestPayload(BaseModel):
    record_id: Optional[int] = None
    alarm_type: Optional[str] = Field(default=None, alias='type')
    alarm_code: Optional[str] = Field(default=None, alias='code')
    alarm_message: Optional[str] = Field(default=None, alias='message')
    alarm_level: int = Field(default=3, ge=0, le=10)


CONTROL_TASK_TYPES = {int(meta[1]) for meta in ACTION_META.values()}
CONTROL_TASK_TYPES.add(TASK_DEFAULT_TYPE)
CONTROL_TASK_TYPES.add(30)

_STAGE_TYPE_MAP = {
    "capture": {friendly_action_type("capture")},
    "control": {
        friendly_action_type("manual.defect_detection"),
        friendly_action_type("manual.defect_detection_secondary"),
        friendly_action_type("manual.check"),
    },
}

def _load_check_settings(session: Session) -> Dict[str, Any]:
    """Load inspection threshold config from manual general settings."""
    store = SettingsStore()
    general = store.fetch_category(session, "general") or {}
    section = general.get("inspection") or general.get("check") or {}
    baseline = float(section.get("baseline") or 0.0)
    alarm_range = float(section.get("alarm_range") or 0.5)
    auto_enabled_raw = section.get("auto_check_enabled")
    auto_enabled = bool(auto_enabled_raw)
    return {
        "baseline": baseline,
        "alarm_range": alarm_range,
        "auto_enabled": auto_enabled,
    }

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


def _latest_stage_task(
    session: Session,
    stage: str,
    record_id: Optional[int],
) -> Optional[HardwareTaskQueue]:
    type_codes = _STAGE_TYPE_MAP.get(stage)
    if not type_codes:
        return None
    stmt = select(HardwareTaskQueue).where(HardwareTaskQueue.task_type.in_(tuple(type_codes)))
    if record_id is not None and record_id > 0:
        stmt = stmt.where(HardwareTaskQueue.record_id == record_id)
    stmt = stmt.order_by(desc(HardwareTaskQueue.id))
    return session.execute(stmt).scalars().first()


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
    return save_data.ensure_record_folder(record_id)


@router.post('/capture')
def create_capture_record(payload: CaptureRequestPayload, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    workpiece = _get_workpiece(session, payload.workpiece_id)
    record = RecordTable(
        workpiece_id=workpiece.id,
        r_progress_data={'stage': 'capture_pending'},
    )
    session.add(record)
    session.flush()

    _ensure_save_dir(record.id)
    session.commit()
    session.refresh(record)
    return {
        'ok': True,
        'record_id': record.id,
        'record': {'id': record.id, 'workpiece_id': record.workpiece_id},
        'workpiece': _serialize_workpiece(workpiece),
    }


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

    record_filter_id: Optional[int] = None
    if record_id is not None and record_id > 0:
        record_filter_id = record_id
    elif record is not None:
        record_filter_id = record.id

    latest_capture = _latest_stage_task(session, "capture", record_filter_id)
    latest_execute = None
    latest_control = _latest_stage_task(session, "control", record_filter_id)

    capture_active = bool(
        latest_capture and latest_capture.status in (int(TaskStatus.PENDING), int(TaskStatus.RUNNING))
    )
    execute_active = False
    control_active = bool(
        latest_control and latest_control.status in (int(TaskStatus.PENDING), int(TaskStatus.RUNNING))
    )

    ready_capture = not capture_active
    ready_execute = ready_capture
    ready_control = not control_active

    control_stmt = select(HardwareTaskQueue).where(
        HardwareTaskQueue.task_type.in_(tuple(CONTROL_TASK_TYPES))
    ).order_by(desc(HardwareTaskQueue.id))
    if record_filter_id is not None and record_filter_id > 0:
        control_stmt = control_stmt.where(HardwareTaskQueue.record_id == record_filter_id)
    control_rows = session.execute(control_stmt).scalars().all()
    control_commands = [_serialize_task(row) for row in control_rows]

    gcode_payload: Any = None
    alg_record_id = record_filter_id if record_filter_id else (record.id if record else None)
    alg_path, alg_json = save_data.load_alg_result(alg_record_id)
    if alg_json:
        try:
            gcode_payload = program.build_program_payload_from_alg_data(alg_json)
            if alg_path:
                gcode_payload["alg_result_path"] = str(alg_path)
        except Exception:
            gcode_payload = {"alg_result": alg_json}

    alarm_summary = _alarm_summary_for_record(session, record.id if record else None)

    return {
        'workpiece': _serialize_workpiece(workpiece) if workpiece else None,
        'latest_record': record.id if record else None,
        'capture': _serialize_task(latest_capture) if latest_capture else None,
        'execute': None,
        'control': _serialize_task(latest_control) if latest_control else None,
        'command_record_id': record_filter_id,
        'command_list': control_commands,
        'ready': {
            'capture': ready_capture,
            'execute': ready_execute,
            'control': ready_control,
            'record_id': record_filter_id if record_filter_id else (record.id if record else None),
        },
        'gcode': gcode_payload,
        'alarm_max_level': alarm_summary['max_level'],
        'alarm_requires_reset': alarm_summary['requires_reset'],
    }


@router.delete('/data/tasks/control/{task_id}')
def delete_control_task(task_id: int, session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    row = session.get(HardwareTaskQueue, task_id)
    if row is None or int(row.task_type or 0) not in CONTROL_TASK_TYPES:
        raise HTTPException(status_code=404, detail='Control task not found')
    session.delete(row)
    session.commit()
    return {'ok': True, 'task_id': task_id}


@router.delete('/data/tasks/control')
def clear_control_tasks(session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    stmt = delete(HardwareTaskQueue).where(HardwareTaskQueue.task_type.in_(tuple(CONTROL_TASK_TYPES)))
    result = session.execute(stmt)
    session.commit()
    return {'ok': True, 'deleted': result.rowcount or 0}




