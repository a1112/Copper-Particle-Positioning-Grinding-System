import datetime
import decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, DECIMAL, Index, Integer, JSON, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class QualityTable(Base):
    __tablename__ = "quality_table"
    __table_args__ = (
        Index("idx_detection_time", "q_detection_time"),
        Index("idx_qualify_status", "q_qualify_status"),
        Index("idx_workpiece_id", "q_workpiece_id"),
        {"comment": "质量检测表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    q_workpiece_id: Mapped[str] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), nullable=False, comment="工件编号"
    )
    q_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="任务ID")
    q_detection_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="检测时间",
    )
    q_roughness: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(5, 3), comment="粗糙度"
    )
    q_defect_count: Mapped[Optional[int]] = mapped_column(Integer, comment="缺陷数量")
    q_defect_details: Mapped[Optional[dict]] = mapped_column(JSON, comment="缺陷详情")
    q_qualify_status: Mapped[Optional[int]] = mapped_column(
        TINYINT, comment="合格状态（0-不合格，1-合格）"
    )
    q_operator: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="检测人员"
    )


__all__ = ["QualityTable"]
