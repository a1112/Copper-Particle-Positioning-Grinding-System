import datetime
import decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, DECIMAL, Index, Integer, JSON, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TaskTable(Base):
    __tablename__ = "task_table"
    __table_args__ = (
        Index("idx_created_time", "created_time"),
        Index("idx_status", "t_status"),
        {"comment": "任务管理表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    t_task_name: Mapped[str] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), nullable=False, comment="任务名称"
    )
    t_task_type: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        comment="任务类型（0-打磨，1-抛光，2-检测，3-维护）",
    )
    t_workpiece_type: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="工件类型"
    )
    t_material_type: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="材料类型"
    )
    t_priority: Mapped[Optional[int]] = mapped_column(
        TINYINT, default=0, server_default=text("'1'"), comment="优先级"
    )
    t_status: Mapped[Optional[int]] = mapped_column(
        TINYINT,
        default=0,
        server_default=text("'0'"),
        comment="",
    )
    t_progress: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(5, 2), server_default=text("'0.00'"), comment="进度百分比"
    )
    t_estimated_time: Mapped[Optional[int]] = mapped_column(Integer, comment="预计耗时(秒)")
    t_actual_time: Mapped[Optional[int]] = mapped_column(Integer, comment="实际耗时(秒)")
    t_workpiece_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, default=None, comment="关联工件ID"
    )
    t_record_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, default=None, comment="关联记录ID"
    )
    t_payload: Mapped[Optional[dict]] = mapped_column(
        JSON, default=None, comment="任务附加参数"
    )
    t_status_detail: Mapped[Optional[dict]] = mapped_column(
        JSON, default=None, comment="状态详情信息"
    )
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间",
    )


__all__ = ["TaskTable"]
