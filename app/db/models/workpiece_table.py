import datetime
import decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, DECIMAL, Index, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class WorkpieceTable(Base):
    __tablename__ = "workpiece_table"
    __table_args__ = (
        Index("idx_status", "w_status"),
        Index("idx_task_id", "w_task_id"),
        Index("uk_workpiece_id", "w_workpiece_id", unique=True),
        {"comment": "工件信息表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    w_workpiece_id: Mapped[str] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), nullable=False, comment="工件编号"
    )
    w_workpiece_type: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="工件类型"
    )
    w_material: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="材料"
    )
    w_dimensions: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment='尺寸 "长,宽,高"'
    )
    w_surface_requirement: Mapped[Optional[str]] = mapped_column(
        String(200, "utf8mb4_unicode_ci"), comment="表面要求"
    )
    w_roughness_required: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(5, 3), default=None, comment="要求粗糙度"
    )
    w_roughness_actual: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(5, 3), default=None, comment="实际粗糙度"
    )
    w_status: Mapped[Optional[int]] = mapped_column(
        TINYINT,
        default=0,
        server_default=text("'0'"),
        comment="状态（0-待加工，1-加工中，2-已完成，3-不合格）",
    )
    w_task_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, default=None, comment="关联任务ID"
    )
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )


__all__ = ["WorkpieceTable"]
