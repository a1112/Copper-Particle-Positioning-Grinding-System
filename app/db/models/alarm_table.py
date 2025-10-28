import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AlarmTable(Base):
    __tablename__ = "alarm_table"
    __table_args__ = (
        Index("idx_record_id", "record_id"),
        Index("idx_alarm_level", "alarm_level"),
        {"comment": "报警信息表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    record_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="关联记录ID")
    alarm_type: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="报警类型"
    )
    alarm_code: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="报警代码"
    )
    alarm_message: Mapped[Optional[str]] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), comment="报警信息"
    )
    alarm_level: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        server_default=text("'0'"),
        comment="报警等级",
    )
    handled_status: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        server_default=text("'0'"),
        comment="处理状态（0-未处理，1-处理中，2-已处理）",
    )
    alarm_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="报警时间",
    )
    handled_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, comment="处理时间"
    )
    handler: Mapped[Optional[str]] = mapped_column(
        String(50, "utf8mb4_unicode_ci"), comment="处理人"
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


__all__ = ["AlarmTable"]
