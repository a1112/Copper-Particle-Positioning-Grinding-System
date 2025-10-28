import datetime
import decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    DECIMAL,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class StatusTable(Base):
    __tablename__ = "status_table"
    __table_args__ = (
        CheckConstraint("(`id` = 1)", name="chk_single_row"),
        {"comment": "状态监控表（单记录）"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        server_default=text("'1'"),
        comment="主键ID，固定为1确保只有一条记录",
    )
    c_run_status: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        server_default=text("'0'"),
        comment="运行状态（0-空闲，1-初始化完成，2-运行，3-暂停，4-停止）",
    )
    c_alarm_status: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        server_default=text("'0'"),
        comment="报警状态（0-无报警，1-有报警）",
    )
    c_control_mode: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        server_default=text("'0'"),
        comment="控制方式（0-本地，1-远程）",
    )
    c_machine_mode: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        server_default=text("'0'"),
        comment="机台模式（0-手动，1-自动，2-单步，3-调试，4-维护）",
    )
    s_temperature: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(5, 2), comment="温度"
    )
    s_spindle_speed: Mapped[Optional[int]] = mapped_column(Integer, comment="主轴转速")
    s_feed_speed: Mapped[Optional[int]] = mapped_column(Integer, comment="进给速度")
    s_point_motion_speed: Mapped[Optional[int]] = mapped_column(Integer, comment="点动速度")
    s_tool_diameter: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(6, 2), comment="刀具直径"
    )
    s_line_spacing: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(6, 2), comment="行刀间距"
    )
    s_total_cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(6, 2), comment="切削总深"
    )
    s_clearance_speed: Mapped[Optional[int]] = mapped_column(Integer, comment="空隙速度")
    s_work_surface_height: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(8, 2), comment="工作表面高度"
    )
    s_cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(6, 2), comment="吃刀深度"
    )
    s_step_distance: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(8, 2), comment="步动距离"
    )
    f_fixture_status: Mapped[Optional[int]] = mapped_column(
        INTEGER, comment="夹具状态（16位二进制，每位代表一个夹具状态）"
    )
    p_absolute_position: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment='绝对坐标 "x,y,z"'
    )
    p_relative_position: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment='相对坐标 "x,y,z"'
    )
    p_work_position: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment='工作坐标 "x,y,z"'
    )
    p_remaining_distance: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment='剩余距离 "x,y,z"'
    )
    status_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="状态时间",
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


__all__ = ["StatusTable"]
