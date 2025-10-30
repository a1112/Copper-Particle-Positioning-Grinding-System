import datetime
import decimal
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, DECIMAL, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CuttingStatusTable(Base):
    __tablename__ = "cutting_status_table"
    __table_args__ = (
        CheckConstraint("(`id` = 1)", name="chk_cutting_single_row"),
        {"comment": "切削状态记录（单行）"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        server_default=text("'1'"),
        comment="主键ID，仅允许存在一条记录",
    )
    feed_rate: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(10, 3),
        nullable=False,
        server_default=text("'0.000'"),
        comment="进给速度(mm/s)",
    )
    elapsed_sec: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(10, 3),
        nullable=False,
        server_default=text("'0.000'"),
        comment="累计执行时长(秒)",
    )
    spindle_rpm: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        server_default=text("'0.00'"),
        comment="主轴转速(rpm)",
    )
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="最近更新时间",
    )
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )


__all__ = ["CuttingStatusTable"]
