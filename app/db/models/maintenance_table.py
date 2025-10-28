import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MaintenanceTable(Base):
    __tablename__ = "maintenance_table"
    __table_args__ = (
        Index("idx_machine_id", "m_machine_id"),
        Index("idx_planned_time", "m_planned_time"),
        Index("idx_status", "m_status"),
        {"comment": "设备维护表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    m_machine_id: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="设备编号"
    )
    m_maintenance_type: Mapped[Optional[int]] = mapped_column(
        TINYINT, comment="维护类型：1-日常，2-周期，3-月度，4-年度"
    )
    m_maintenance_content: Mapped[Optional[str]] = mapped_column(
        Text(collation="utf8mb4_unicode_ci"), comment="维护内容"
    )
    m_maintenance_person: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="维护人员"
    )
    m_planned_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, comment="计划时间"
    )
    m_actual_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, comment="实际时间"
    )
    m_status: Mapped[Optional[int]] = mapped_column(
        TINYINT,
        default=0,
        server_default=text("'0'"),
        comment="状态（0-待执行，1-执行中，2-已完成）",
    )
    m_remark: Mapped[Optional[str]] = mapped_column(
        Text(collation="utf8mb4_unicode_ci"), comment="备注"
    )
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )


__all__ = ["MaintenanceTable"]
