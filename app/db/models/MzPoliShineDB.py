from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, CheckConstraint, DECIMAL, DateTime, Index, Integer, JSON, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class ActionTable(Base):
    __tablename__ = 'action_table'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_priority', 'priority'),
        Index('idx_status', 'status'),
        {'comment': '动作表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    action_name: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False, comment='动作名称')
    command: Mapped[str] = mapped_column(String(500, 'utf8mb4_unicode_ci'), nullable=False, comment='指令')
    status: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='状态（0-待执行，1-执行中，2-已完成，3-失败）')
    priority: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'1'"), comment='优先级（1-低，2-中，3-高）')
    execute_times: Mapped[Optional[int]] = mapped_column(Integer, default=0, server_default=text("'0'"), comment='执行次数')
    max_retries: Mapped[Optional[int]] = mapped_column(Integer, default=3, server_default=text("'3'"), comment='最大重试次数')
    error_message: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='错误信息')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class HardwareTaskQueue(Base):
    __tablename__ = 'hardware_task_queue'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_device_status', 'device_id', 'status'),
        Index('idx_execute_time', 'execute_time'),
        Index('idx_status', 'status'),
        Index('task_id', 'task_id', unique=True),
        {'comment': '硬件控制任务轮询表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    task_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment='任务唯一标识')
    task_type: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, comment='任务类型：POLISH_START/ POLISH_STOP/ TEMPERATURE_SET/ PRESSURE_ADJUST等')
    device_id: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, comment='设备标识')
    task_params: Mapped[Optional[dict]] = mapped_column(JSON, default=None, comment='任务参数，JSON格式')
    priority: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'0'"), comment='优先级：0-普通 1-高 2-紧急')
    status: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'0'"), comment='状态：0-待执行 1-执行中 2-执行成功 3-执行失败 4-已取消')
    retry_count: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'0'"), comment='重试次数')
    max_retry_count: Mapped[Optional[int]] = mapped_column(TINYINT, default=3, server_default=text("'3'"), comment='最大重试次数')
    execute_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=None, server_default=text('CURRENT_TIMESTAMP'), comment='计划执行时间')
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=None, comment='实际开始时间')
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=None, comment='实际结束时间')
    result_message: Mapped[Optional[str]] = mapped_column(TEXT, default=None, comment='执行结果信息')
    created_by: Mapped[Optional[str]] = mapped_column(VARCHAR(50), default=None, comment='创建者')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class MaintenanceTable(Base):
    __tablename__ = 'maintenance_table'
    __table_args__ = (
        Index('idx_machine_id', 'm_machine_id'),
        Index('idx_planned_time', 'm_planned_time'),
        Index('idx_status', 'm_status'),
        {'comment': '设备维护表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    m_machine_id: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='设备编号')
    m_maintenance_type: Mapped[Optional[int]] = mapped_column(TINYINT, comment='维护类型（0-日常，1-周常，2-月常，3-年度）')
    m_maintenance_content: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='维护内容')
    m_maintenance_person: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='维护人员')
    m_planned_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='计划时间')
    m_actual_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='实际时间')
    m_status: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'0'"), comment='状态（0-待执行，1-执行中，2-已完成）')
    m_remark: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='备注')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')


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
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'1'"), comment='是否激活（1-激活，0-禁用）')
    created_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='创建人')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='更新人')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class ParamMachine(Base):
    __tablename__ = 'param_machine'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_is_active', 'is_active'),
        Index('idx_setting_name', 'setting_name'),
        {'comment': '机台参数表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, server_default=text("'1'"), comment='主键ID，固定为1确保只有一条记录')
    s_BasicSettings: Mapped[Optional[dict]] = mapped_column(JSON, comment='基础设置')
    s_PointSettings: Mapped[Optional[dict]] = mapped_column(JSON, comment='点位设置')
    s_DeviceBehavior: Mapped[Optional[dict]] = mapped_column(JSON, comment='设备行为')
    s_ToolParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='刀具参数')
    s_FixtureParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='夹具参数')
    s_WorkpieceParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='工件参数')
    s_ProcessParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='工艺参数')
    s_MachineInfo: Mapped[Optional[dict]] = mapped_column(JSON, comment='机台信息')
    s_CameraParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='相机参数')
    s_DatabaseParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='数据库参数')
    setting_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='配置名称')
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='配置描述')
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'1'"), comment='是否激活（1-激活，0-禁用）')
    created_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='创建人')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='更新人')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class ProcessHistory(Base):
    __tablename__ = 'process_history'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_task_id', 'ph_task_id'),
        Index('idx_workpiece_id', 'ph_workpiece_id'),
        {'comment': '工艺参数历史表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    ph_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment='任务ID')
    ph_workpiece_id: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='工件ID')
    ph_parameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='工艺参数快照')
    ph_result: Mapped[Optional[dict]] = mapped_column(JSON, comment='加工结果')
    ph_quality_score: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2), comment='质量评分')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')


class QualityTable(Base):
    __tablename__ = 'quality_table'
    __table_args__ = (
        Index('idx_detection_time', 'q_detection_time'),
        Index('idx_qualify_status', 'q_qualify_status'),
        Index('idx_workpiece_id', 'q_workpiece_id'),
        {'comment': '质量检测表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    q_workpiece_id: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'), nullable=False, comment='工件编号')
    q_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment='任务ID')
    q_detection_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='检测时间')
    q_roughness: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 3), comment='粗糙度')
    q_defect_count: Mapped[Optional[int]] = mapped_column(Integer, comment='缺陷数量')
    q_defect_details: Mapped[Optional[dict]] = mapped_column(JSON, comment='缺陷详情')
    q_qualify_status: Mapped[Optional[int]] = mapped_column(TINYINT, comment='合格状态（0-不合格，1-合格）')
    q_operator: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='检测人员')


class RecordTable(Base):
    __tablename__ = 'record_table'
    __table_args__ = (
        Index('idx_record_time', 'record_time'),
        {'comment': '记录表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    r_progress_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='进度数据')
    r_camera_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='相机数据')
    r_algorithm_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='算法数据')
    r_machine_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='机台数据')
    r_warning_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='警告数据')
    record_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='记录时间')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')


class StatusTable(Base):
    __tablename__ = 'status_table'
    __table_args__ = (
        CheckConstraint('(`id` = 1)', name='chk_single_row'),
        {'comment': '状态监控表（单记录）'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, server_default=text("'1'"), comment='主键ID，固定为1确保只有一条记录')
    c_run_status: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='运行状态（0-空闲，1-初始化完成，2-运行，3-暂停，4-停止）')
    c_alarm_status: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='报警状态（0-无报警，1-有报警）')
    c_control_mode: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='控制方式（0-本地，1-远程）')
    c_machine_mode: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='机台模式（0-手动，1-自动，2-单步，3-调试，4-维护）')
    s_temperature: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2), comment='温度')
    s_spindle_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='主轴转速')
    s_feed_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='进给速度')
    s_point_motion_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='点动速度')
    s_tool_diameter: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='刀具直径')
    s_line_spacing: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='行刀间距')
    s_total_cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='切削总深')
    s_clearance_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='空隙速度')
    s_work_surface_height: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 2), comment='工作表面高度')
    s_cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='吃刀深度')
    s_step_distance: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 2), comment='步动距离')
    f_fixture_status: Mapped[Optional[int]] = mapped_column(INTEGER, comment='夹具状态（16位二进制，每位代表一个夹具状态）')
    p_absolute_position: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='绝对坐标 "x,y,z"')
    p_relative_position: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='相对坐标 "x,y,z"')
    p_work_position: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='工作坐标 "x,y,z"')
    p_remaining_distance: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='剩余距离 "x,y,z"')
    status_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='状态时间')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class TaskTable(Base):
    __tablename__ = 'task_table'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_status', 't_status'),
        {'comment': '任务管理表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    t_task_name: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False, comment='任务名称')
    t_task_type: Mapped[int] = mapped_column(TINYINT, nullable=False, comment='任务类型（0-打磨，1-抛光，2-检测，3-维护）')
    t_workpiece_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='工件类型')
    t_material_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='材料类型')
    t_priority: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'1'"), comment='优先级')
    t_status: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'0'"), comment='任务状态（0-待执行，1-执行中，2-已完成，3-暂停，4-取消）')
    t_progress: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2), server_default=text("'0.00'"), comment='进度百分比')
    t_estimated_time: Mapped[Optional[int]] = mapped_column(Integer, comment='预计耗时(秒)')
    t_actual_time: Mapped[Optional[int]] = mapped_column(Integer, comment='实际耗时(秒)')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class WorkpieceTable(Base):
    __tablename__ = 'workpiece_table'
    __table_args__ = (
        Index('idx_status', 'w_status'),
        Index('idx_task_id', 'w_task_id'),
        Index('uk_workpiece_id', 'w_workpiece_id', unique=True),
        {'comment': '工件信息表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    w_workpiece_id: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'), nullable=False, comment='工件编号')
    w_workpiece_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='工件类型')
    w_material: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='材料')
    w_dimensions: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='尺寸 "长,宽,高"')
    w_surface_requirement: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb4_unicode_ci'), comment='表面要求')
    w_roughness_required: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 3), default=None, comment='要求粗糙度')
    w_roughness_actual: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 3), default=None, comment='实际粗糙度')
    w_status: Mapped[Optional[int]] = mapped_column(TINYINT, default=0, server_default=text("'0'"), comment='状态（0-待加工，1-加工中，2-已完成，3-不合格）')
    w_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, default=None, comment='关联任务ID')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
