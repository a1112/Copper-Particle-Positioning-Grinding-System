from typing import Optional
import datetime
import decimal

from sqlalchemy import DECIMAL, Float, Index, Integer, JSON, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import ENUM, TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

class Base(MappedAsDataclass, DeclarativeBase):
    pass


class ActionCommands(Base):
    __tablename__ = 'action_commands'
    __table_args__ = (
        Index('idx_action_priority', 'priority'),
        Index('idx_action_status', 'status'),
        Index('idx_created_at', 'created_at')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_name: Mapped[str] = mapped_column(String(200, 'utf8mb4_unicode_ci'), nullable=False, comment='动作名称')
    command_code: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='指令代码')
    command_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='指令数据')
    status: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='0=未执行, 1=执行成功, -1=执行失败, 2=执行中')
    priority: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='优先级')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    executed_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, comment='执行时间')
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, comment='完成时间')
    error_message: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='错误信息')


class CameraConfig(Base):
    __tablename__ = 'camera_config'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    camera_id: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False, comment='相机标识')
    resolution_width: Mapped[Optional[int]] = mapped_column(Integer, comment='分辨率宽')
    resolution_height: Mapped[Optional[int]] = mapped_column(Integer, comment='分辨率高')
    frame_rate: Mapped[Optional[int]] = mapped_column(Integer, comment='帧率')
    exposure_time: Mapped[Optional[float]] = mapped_column(Float, comment='曝光时间')
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='厂商名')
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"), comment='是否激活')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class CoordinateSystem(Base):
    __tablename__ = 'coordinate_system'
    __table_args__ = (
        Index('idx_coordinate_type', 'coordinate_type'),
        Index('idx_timestamp', 'timestamp')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    coordinate_type: Mapped[str] = mapped_column(ENUM('绝对位置', '相对位置', '工件位置', '剩余距离'), nullable=False)
    x_position: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 3), nullable=False, comment='X坐标(mm)')
    y_position: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 3), nullable=False, comment='Y坐标(mm)')
    z_position: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 3), nullable=False, comment='Z坐标(mm)')
    timestamp: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


class FixtureStatus(Base):
    __tablename__ = 'fixture_status'
    __table_args__ = (
        Index('unique_fixture', 'fixture_id', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fixture_id: Mapped[int] = mapped_column(TINYINT, nullable=False, comment='夹具编号1~16')
    is_on: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='开关状态: true=开, false=关')
    position_x: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='X坐标')
    position_y: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='Y坐标')
    position_z: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='Z坐标')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class RunningLog(Base):
    __tablename__ = 'running_log'
    __table_args__ = (
        Index('idx_job_id', 'job_id'),
        Index('idx_progress', 'progress'),
        Index('idx_start_time', 'start_time'),
        Index('job_id', 'job_id', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    progress: Mapped[str] = mapped_column(ENUM('未执行', '相机取图', '算法调用', '指令执行', '完成'), nullable=False, server_default=text("'未执行'"))
    job_id: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='任务唯一标识')
    camera_image_path: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb4_unicode_ci'), comment='图像保存路径')
    algorithm_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='算法相关数据')
    machine_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='机台数据')
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, comment='开始时间')
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, comment='结束时间')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


class SpindleMotor(Base):
    __tablename__ = 'spindle_motor'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, comment='温度')
    spindle_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='主轴转速')
    tool_diameter: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='刀具直径(mm)')
    tool_path_spacing: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='行刀间距(mm)')
    total_cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='切削总深(mm)')
    air_cutting_speed: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='空跑速度(mm/s)')
    workpiece_surface_height: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='工件表面高度(mm)')
    cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='吃刀深度(mm)')
    step_distance: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='步动距离(mm)')
    feed_rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='进给速度(mm/s)')
    jog_speed: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 3), comment='点动速度(mm/s)')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class SystemParameters(Base):
    __tablename__ = 'system_parameters'
    __table_args__ = (
        Index('unique_param', 'category', 'parameter_name', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'), nullable=False, comment='参数类别')
    parameter_name: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False, comment='参数名称')
    data_type: Mapped[str] = mapped_column(ENUM('int', 'float', 'string', 'bool', 'array'), nullable=False, server_default=text("'string'"))
    parameter_value: Mapped[Optional[dict]] = mapped_column(JSON, comment='参数值')
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='参数描述')
    is_editable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"), comment='是否可编辑')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class SystemStatus(Base):
    __tablename__ = 'system_status'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    running_status: Mapped[str] = mapped_column(ENUM('运行', '暂停', '报警', '空闲', '初始化完成'), nullable=False, server_default=text("'空闲'"))
    communication_status: Mapped[str] = mapped_column(ENUM('运行', '停止'), nullable=False, server_default=text("'停止'"))
    alarm_status: Mapped[str] = mapped_column(ENUM('报警', '无'), nullable=False, server_default=text("'无'"))
    control_mode: Mapped[str] = mapped_column(ENUM('远程', '本地'), nullable=False, server_default=text("'本地'"))
    machine_mode: Mapped[str] = mapped_column(ENUM('点动', '手动', '自动'), nullable=False, server_default=text("'手动'"))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class WarningLog(Base):
    __tablename__ = 'warning_log'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='描述')
    error_code: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='错误码')
    solution: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='解决方法')
    triggered_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='触发时间')
    processed_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, comment='处理时间')
    is_processed: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'0'"), comment='是否已处理')
