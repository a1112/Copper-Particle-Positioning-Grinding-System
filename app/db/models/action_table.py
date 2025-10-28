import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ActionTable(Base):
    __tablename__ = "action_table"
    __table_args__ = (
        Index("idx_created_time", "created_time"),
        Index("idx_priority", "priority"),
        Index("idx_status", "status"),
        {"comment": "动作表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    action_name: Mapped[str] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), nullable=False, comment="动作名称"
    )
    command: Mapped[str] = mapped_column(
        String(500, "utf8mb4_unicode_ci"), nullable=False, comment="指令"
    )
    status: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        server_default=text("'0'"),
        comment="状态（0-待执行，1-执行中，2-已完成，3-失败）",
    )
    priority: Mapped[Optional[int]] = mapped_column(
        TINYINT,
        default=0,
        server_default=text("'1'"),
        comment="优先级（1-低，2-中，3-高）",
    )
    execute_times: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0,
        server_default=text("'0'"),
        comment="执行次数",
    )
    max_retries: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=3,
        server_default=text("'3'"),
        comment="最大重试次数",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text(collation="utf8mb4_unicode_ci"), comment="错误信息"
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


__all__ = ["ActionTable"]
