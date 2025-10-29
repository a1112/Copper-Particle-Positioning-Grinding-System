import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class HardwareTaskQueue(Base):
    __tablename__ = 'hardware_task_queue'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_device_status', 'device_id', 'status'),
        Index('idx_execute_time', 'execute_time'),
        Index('idx_status', 'status'),
        {'comment': '硬件控制任务轮询表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    workpiece_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, default=None, comment="关联工件ID"
    )
    record_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, default=None, comment="关联记录ID"
    )
    task_name: Mapped[str] = mapped_column(String(64, 'utf8mb4_unicode_ci'), nullable=False, comment='任务名称')
    task_type: Mapped[int] = mapped_column(Integer, nullable=False, comment='任务类型')
    device_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='设备标识ID')
    task_params: Mapped[Optional[dict]] = mapped_column(JSON, comment='任务参数，JSON格式')
    priority: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("'0'"), comment='优先级：0-普通 1-高 2-紧急')
    status: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("'0'"), comment='状态：0-待执行 1-执行中 2-执行成功 3-执行失败 4-已取消')
    status_params: Mapped[Optional[dict]] = mapped_column(JSON, comment='任务状态，JSON格式')
    retry_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("'0'"), comment='重试次数')
    max_retry_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("'3'"), comment='最大重试次数')
    execute_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='计划执行时间')
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='实际开始时间')
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='实际结束时间')
    result_message: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='执行结果信息')
    created_by: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='创建者')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')



__all__ = ["HardwareTaskQueue"]
