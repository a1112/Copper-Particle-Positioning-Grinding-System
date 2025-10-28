import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, JSON, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ParamAlgorithm(Base):
    __tablename__ = 'param_algorithm'
    __table_args__ = (
        Index('idx_algorithm_name', 'algorithm_name'),
        Index('idx_created_time', 'created_time'),
        Index('idx_is_active', 'is_active'),
        {'comment': '算法参数表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, server_default=text("'1'"), comment='主键ID，固定为1确保只有一条记录')
    s_PreProcess3DSPara: Mapped[dict] = mapped_column(JSON, nullable=False, comment='预处理参数')
    s_DefectPlateBPara: Mapped[dict] = mapped_column(JSON, nullable=False, comment='缺陷参数')
    s_JggyPara: Mapped[dict] = mapped_column(JSON, nullable=False, comment='路径规划参数')
    algorithm_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='算法名称')
    algorithm_version: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), server_default=text("'1.0'"), comment='算法版本')
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='参数描述')
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'1'"), comment='是否激活（1-激活，0-禁用）')
    created_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='创建人')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='更新人')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')




__all__ = ["ParamAlgorithm"]
