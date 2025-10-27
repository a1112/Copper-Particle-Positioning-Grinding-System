from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.db.models.MzPoliShineDB import RecordTable, TaskTable, WorkpieceTable
from app.server.api.api_core import data_router as router
from app.common.tasks import TaskStatus, TaskType
from app import config

SAVE_DATA_DIR = Path(config.PROJECT_ROOT) / 'SaveData'


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


def _serialize_task(row: TaskTable) -> Dict[str, Any]:
    return {
        'id': row.id,
        'name': row.t_task_name,
        'type': row.t_task_type,
        'status': row.t_status,
        'workpiece_id': row.t_workpiece_id,
        'record_id': row.t_record_id,
        'payload': row.t_payload or {},
        'status_detail': row.t_status_detail or {},
        'created_time': row.created_time.isoformat() if row.created_time else None,
        'updated_time': row.updated_time.isoformat() if row.updated_time else None,
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
    task = TaskTable(
        t_task_name=f'capture-{record.id}',
        t_task_type=int(TaskType.CAPTURE),
        t_workpiece_type=workpiece.w_workpiece_type,
        t_material_type=workpiece.w_material,
        t_status=int(TaskStatus.PENDING),
        t_workpiece_id=workpiece.id,
        t_record_id=record.id,
        t_payload={'folder': str(folder), 'note': payload.note or ''},
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
    task = TaskTable(
        t_task_name=f'execute-{record.id}',
        t_task_type=int(TaskType.EXECUTE),
        t_workpiece_id=record.workpiece_id,
        t_record_id=record.id,
        t_status=int(TaskStatus.PENDING),
        t_payload={'record_id': record.id},
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return {'ok': True, 'task': _serialize_task(task)}


def _latest_task(session: Session, task_type: TaskType) -> Optional[TaskTable]:
    return (
        session.execute(
            select(TaskTable)
            .where(TaskTable.t_task_type == int(task_type))
            .order_by(desc(TaskTable.id))
        )
        .scalars()
        .first()
    )


@router.get('/data/tasks/state')
def task_state_summary(session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    workpiece = _ensure_default_workpiece(session)
    record = session.execute(select(RecordTable).order_by(desc(RecordTable.id))).scalars().first()

    latest_capture = _latest_task(session, TaskType.CAPTURE)
    latest_execute = _latest_task(session, TaskType.EXECUTE)
    latest_control = _latest_task(session, TaskType.CONTROL)

    capture_active = latest_capture and latest_capture.t_status in (int(TaskStatus.PENDING), int(TaskStatus.RUNNING))
    execute_active = latest_execute and latest_execute.t_status in (int(TaskStatus.PENDING), int(TaskStatus.RUNNING))
    capture_ready = bool(latest_capture and latest_capture.t_status == int(TaskStatus.COMPLETED))
    execute_ready = capture_ready and not execute_active

    return {
        'workpiece': _serialize_workpiece(workpiece) if workpiece else None,
        'latest_record': record.id if record else None,
        'capture': _serialize_task(latest_capture) if latest_capture else None,
        'execute': _serialize_task(latest_execute) if latest_execute else None,
        'control': _serialize_task(latest_control) if latest_control else None,
        'ready': {
            'capture': not bool(capture_active),
            'execute': execute_ready,
            'record_id': record.id if record else None,
        },
    }
