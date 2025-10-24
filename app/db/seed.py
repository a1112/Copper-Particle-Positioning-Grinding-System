from __future__ import annotations

import logging
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.db.models.tool import ToolRecord

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
