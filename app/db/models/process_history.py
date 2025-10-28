import datetime
import decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, DECIMAL, Index, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ProcessHistory(Base):
    __tablename__ = "process_history"
    __table_args__ = (
        Index("idx_created_time", "created_time"),
        Index("idx_task_id", "ph_task_id"),
        Index("idx_workpiece_id", "ph_workpiece_id"),
        {"comment": "工艺参数历史表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    ph_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="任务ID")
    ph_workpiece_id: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="工件ID"
    )
    ph_parameters: Mapped[Optional[dict]] = mapped_column(JSON, comment="工艺参数快照")
    ph_result: Mapped[Optional[dict]] = mapped_column(JSON, comment="加工结果")
    ph_quality_score: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(5, 2), comment="质量评分"
    )
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )


__all__ = ["ProcessHistory"]
