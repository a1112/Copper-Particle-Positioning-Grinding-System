from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ParamSettings(Base):
    __tablename__ = "param_settings"
    __table_args__ = (
        Index("idx_param_category", "category", unique=True),
        {'comment': 'UI 参数配置表，每个类别仅保留一条记录'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, comment="配置类别标识")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, comment="配置内容JSON")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
    updated_by: Mapped[Optional[str]] = mapped_column(String(100), comment="最后更新人")


__all__ = ["ParamSettings"]
