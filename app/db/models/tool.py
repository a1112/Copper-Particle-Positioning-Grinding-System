from __future__ import annotations

import datetime

from sqlalchemy import DECIMAL, Integer, SmallInteger, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ToolRecord(Base):
    __tablename__ = "tool_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False, comment="刀具型号")
    diameter_mm: Mapped[float] = mapped_column(
        DECIMAL(8, 3), nullable=False, comment="刀具直径(mm)"
    )
    length_mm: Mapped[float] = mapped_column(
        DECIMAL(8, 3), nullable=False, comment="刀具长度(mm)"
    )
    usage_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0"), comment="累计使用时间(分钟)"
    )
    service_life_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0"), comment="设计寿命(分钟)"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0"), comment="使用状态"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "model": self.model,
            "diameter_mm": float(self.diameter_mm) if self.diameter_mm is not None else None,
            "length_mm": float(self.length_mm) if self.length_mm is not None else None,
            "usage_minutes": self.usage_minutes,
            "service_life_minutes": self.service_life_minutes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

