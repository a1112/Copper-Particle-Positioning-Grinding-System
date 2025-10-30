from __future__ import annotations

import decimal
import logging
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.db.models.MzPoliShineDB import CuttingStatusTable, StatusTable, WorkpieceTable
from app.db.models.tool_record import ToolRecord

LOG = logging.getLogger(__name__)


def _default_tools() -> Sequence[ToolRecord]:
    return [
        ToolRecord(
            model="CP-OPT-120",
            diameter_mm=12.0,
            length_mm=150.0,
            usage_minutes=0,
            service_life_minutes=600,
            status=0,
        ),
        ToolRecord(
            model="CP-OPT-080",
            diameter_mm=8.0,
            length_mm=120.0,
            usage_minutes=45,
            service_life_minutes=480,
            status=1,
        ),
        ToolRecord(
            model="CP-OPT-060",
            diameter_mm=6.0,
            length_mm=100.0,
            usage_minutes=300,
            service_life_minutes=420,
            status=2,
        ),
    ]


def seed_tool_data(session_factory: Iterable[Session] | None = None) -> None:
    """Populate tool_list with sample data when empty."""

    factory = session_factory or SessionLocal
    session: Session | None = None
    try:
        session = factory() if callable(factory) else next(iter(factory))
        exists = session.execute(select(ToolRecord.id).limit(1)).first()
        if exists:
            return
        records = list(_default_tools())
        session.add_all(records)
        session.commit()
        LOG.info("Seeded %d tool records into tool_list", len(records))
    except Exception as exc:
        if session is not None:
            session.rollback()
        LOG.warning("Tool data seeding failed: %s", exc, exc_info=False)
    finally:
        if session is not None:
            session.close()


def _default_workpiece() -> WorkpieceTable:
    return WorkpieceTable(
        w_workpiece_id="WP-DEMO-0001",
        w_workpiece_type="DEMO",
        w_material="Copper",
        w_dimensions="100,100,10",
        w_surface_requirement="Ra <= 0.2",
        w_roughness_required=decimal.Decimal("0.200"),
        w_roughness_actual=decimal.Decimal("0.000"),
        w_status=0,
    )


def seed_workpiece_data(session_factory: Iterable[Session] | None = None) -> None:
    """Ensure workpiece_table has at least one demo row."""

    factory = session_factory or SessionLocal
    session: Session | None = None
    try:
        session = factory() if callable(factory) else next(iter(factory))
        exists = session.execute(select(WorkpieceTable.id).limit(1)).first()
        if exists:
            return
        record = _default_workpiece()
        session.add(record)
        session.commit()
        LOG.info("Seeded default workpiece record id=%s code=%s", record.id, record.w_workpiece_id)
    except Exception as exc:
        if session is not None:
            session.rollback()
        LOG.warning("Workpiece data seeding failed: %s", exc, exc_info=False)
    finally:
        if session is not None:
            session.close()


def _default_status() -> StatusTable:
    return StatusTable(
        id=1,
        c_run_status=0,
        c_alarm_status=0,
        c_control_mode=0,
        c_machine_mode=0,
        s_temperature=decimal.Decimal("0.00"),
        torque=decimal.Decimal("0.000"),
        s_spindle_speed=0,
        s_feed_speed=0,
        s_point_motion_speed=0,
        s_tool_diameter=decimal.Decimal("0.00"),
        s_line_spacing=decimal.Decimal("0.00"),
        s_total_cutting_depth=decimal.Decimal("0.00"),
        s_clearance_speed=0,
        s_work_surface_height=decimal.Decimal("0.00"),
        s_cutting_depth=decimal.Decimal("0.00"),
        s_step_distance=decimal.Decimal("0.00"),
        f_fixture_status=0,
        p_absolute_position="0,0,0",
        p_relative_position="0,0,0",
        p_work_position="0,0,0",
        p_remaining_distance="0,0,0",
        data={},
    )


def seed_status_data(session_factory: Iterable[Session] | None = None) -> None:
    """Ensure status_table contains its singleton monitoring record."""

    factory = session_factory or SessionLocal
    session: Session | None = None
    try:
        session = factory() if callable(factory) else next(iter(factory))
        exists = session.execute(select(StatusTable.id).limit(1)).first()
        if exists:
            return
        record = _default_status()
        session.add(record)
        session.commit()
        LOG.info("Seeded default status record id=%s", record.id)
    except Exception as exc:
        if session is not None:
            session.rollback()
        LOG.warning("Status data seeding failed: %s", exc, exc_info=False)
    finally:
        if session is not None:
            session.close()


def _default_cutting_status() -> CuttingStatusTable:
    return CuttingStatusTable(
        id=1,
        feed_rate=decimal.Decimal("0.000"),
        elapsed_sec=decimal.Decimal("0.000"),
        spindle_rpm=decimal.Decimal("0.00"),
    )


def seed_cutting_status_data(session_factory: Iterable[Session] | None = None) -> None:
    """Ensure cutting_status_table contains a default row required by status polling."""

    factory = session_factory or SessionLocal
    session: Session | None = None
    try:
        session = factory() if callable(factory) else next(iter(factory))
        exists = session.execute(select(CuttingStatusTable.id).limit(1)).first()
        if exists:
            return
        record = _default_cutting_status()
        session.add(record)
        session.commit()
        LOG.info("Seeded default cutting status record id=%s", record.id)
    except Exception as exc:
        if session is not None:
            session.rollback()
        LOG.warning("Cutting status data seeding failed: %s", exc, exc_info=False)
    finally:
        if session is not None:
            session.close()
