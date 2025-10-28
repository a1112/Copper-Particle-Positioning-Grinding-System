import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, JSON, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RecordTable(Base):
    __tablename__ = 'record_table'
    __table_args__ = (
        Index('idx_record_time', 'record_time'),
        {'comment': '记录表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    workpiece_id = mapped_column(BigInteger, comment='workpiece_id')
    r_progress_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='进度数据')
    r_camera_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='相机数据')
    r_algorithm_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='算法数据')
    r_machine_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='机台数据')
    r_warning_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='警告数据')
    record_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='记录时间')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')



__all__ = ["RecordTable"]
