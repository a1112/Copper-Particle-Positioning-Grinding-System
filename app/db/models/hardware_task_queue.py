import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, JSON, text
from sqlalchemy.dialects.mysql import TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class HardwareTaskQueue(Base):
    __tablename__ = "hardware_task_queue"
    __table_args__ = (
        Index("idx_created_time", "created_time"),
        Index("idx_device_status", "device_id", "status"),
        Index("idx_execute_time", "execute_time"),
        Index("idx_status", "status"),
        Index("task_id", "task_id", unique=True),
        {"comment": "硬件控制任务轮询表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    task_id: Mapped[str] = mapped_column(
        VARCHAR(64), nullable=False, comment="任务唯一标识"
    )
    task_type: Mapped[str] = mapped_column(
        VARCHAR(50),
        nullable=False,
        comment="任务类型：POLISH_START/ POLISH_STOP/ TEMPERATURE_SET/ PRESSURE_ADJUST等",
    )
    device_id: Mapped[str] = mapped_column(
        VARCHAR(50), nullable=False, comment="设备标识"
    )
    task_params: Mapped[Optional[dict]] = mapped_column(
        JSON, default=None, comment="任务参数，JSON格式"
    )
    priority: Mapped[Optional[int]] = mapped_column(
        TINYINT,
        default=0,
        server_default=text("'0'"),
        comment="优先级：0-普通 1-高 2-紧急",
    )
    status: Mapped[Optional[int]] = mapped_column(
        TINYINT,
        default=0,
        server_default=text("'0'"),
        comment="状态：0-待执行 1-执行中 2-执行成功 3-执行失败 4-已取消",
    )
    retry_count: Mapped[Optional[int]] = mapped_column(
        TINYINT, default=0, server_default=text("'0'"), comment="重试次数"
    )
    max_retry_count: Mapped[Optional[int]] = mapped_column(
        TINYINT, default=3, server_default=text("'3'"), comment="最大重试次数"
    )
    execute_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        default=None,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="计划执行时间",
    )
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, default=None, comment="实际开始时间"
    )
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, default=None, comment="实际结束时间"
    )
    result_message: Mapped[Optional[str]] = mapped_column(
        TEXT, default=None, comment="执行结果信息"
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        VARCHAR(50), default=None, comment="创建者"
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


__all__ = ["HardwareTaskQueue"]
