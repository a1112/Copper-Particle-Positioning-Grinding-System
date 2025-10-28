import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, JSON, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ParamMachine(Base):
    __tablename__ = "param_machine"
    __table_args__ = (
        Index("idx_created_time", "created_time"),
        Index("idx_is_active", "is_active"),
        Index("idx_setting_name", "setting_name"),
        {"comment": "机台参数表"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        server_default=text("'1'"),
        comment="主键ID，固定为1确保只有一条记录",
    )
    s_BasicSettings: Mapped[Optional[dict]] = mapped_column(JSON, comment="基础设置")
    s_PointSettings: Mapped[Optional[dict]] = mapped_column(JSON, comment="点位设置")
    s_DeviceBehavior: Mapped[Optional[dict]] = mapped_column(JSON, comment="设备行为")
    s_ToolParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment="刀具参数")
    s_FixtureParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment="夹具参数")
    s_WorkpieceParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment="工件参数")
    s_ProcessParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment="工艺参数")
    s_MachineInfo: Mapped[Optional[dict]] = mapped_column(JSON, comment="机台信息")
    s_CameraParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment="相机参数")
    s_DatabaseParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment="数据库参数")
    setting_name: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment="配置名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text(collation="utf8mb4_unicode_ci"), comment="配置描述"
    )
    is_active: Mapped[Optional[int]] = mapped_column(
        TINYINT,
        default=0,
        server_default=text("'1'"),
        comment="是否激活（1-激活，0-禁用）",
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment="创建人"
    )
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(100, "utf8mb4_unicode_ci"), comment="更新人"
    )
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间",
    )


__all__ = ["ParamMachine"]
