from __future__ import annotations

import datetime

from sqlalchemy import BigInteger, Index, SmallInteger, Text
from sqlalchemy.dialects.mysql import DATETIME as MySQLDateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SystemLog(Base):
    __tablename__ = "system_logs"
    __table_args__ = (
        Index("idx_time", "log_time"),
        Index("idx_log_type", "log_type"),
        Index("idx_info_type", "info_type"),
        Index("idx_time_type", "log_time", "log_type", "info_type"),
        {"comment": "系统日志表"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    log_time: Mapped[datetime.datetime] = mapped_column(
        MySQLDateTime(fsp=3), nullable=False, comment="日志时间(精确到毫秒)"
    )
    log_type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="日志类型(1:DEBUG 2:INFO 3:SUCCESS 4:WARNING 5:ERROR)",
    )
    info_type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="信息类型(1:系统 2:数据库 3:设备 4:相机 5:图像处理 6:路径规划 7:指令执行 8:夹具控制)",
    )
    content: Mapped[str] = mapped_column(
        Text(collation="utf8mb4_unicode_ci"), nullable=False, comment="日志内容"
    )


__all__ = ["SystemLog"]