from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, CheckConstraint, DECIMAL, DateTime, ForeignKey, Index, Integer, JSON, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

class Base(MappedAsDataclass, DeclarativeBase):
    pass


class ActionTable(Base):
    __tablename__ = 'action_table'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_priority', 'priority'),
        Index('idx_status', 'status'),
        {'comment': '鍔ㄤ綔琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='涓婚敭ID')
    action_name: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False, comment='鍔ㄤ綔鍚嶇О')
    command: Mapped[str] = mapped_column(String(500, 'utf8mb4_unicode_ci'), nullable=False, comment='鎸囦护')
    status: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='鐘舵€侊紙0-寰呮墽琛岋紝1-鎵ц涓紝2-宸插畬鎴愶紝3-澶辫触锛?)
    priority: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'1'"), comment='浼樺厛绾э紙1-浣庯紝2-涓紝3-楂橈級')
    execute_times: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("'0'"), comment='鎵ц娆℃暟')
    max_retries: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("'3'"), comment='鏈€澶ч噸璇曟鏁?)
    error_message: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='閿欒淇℃伅')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='鏇存柊鏃堕棿')


class HardwareTaskQueue(Base):
    __tablename__ = 'hardware_task_queue'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_device_status', 'device_id', 'status'),
        Index('idx_execute_time', 'execute_time'),
        Index('idx_status', 'status'),
        Index('task_id', 'task_id', unique=True),
        {'comment': '纭欢鎺у埗浠诲姟杞琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='涓婚敭ID')
    task_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, comment='浠诲姟鍞竴鏍囪瘑')
    task_type: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, comment='浠诲姟绫诲瀷锛歅OLISH_START/ POLISH_STOP/ TEMPERATURE_SET/ PRESSURE_ADJUST绛?)
    device_id: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, comment='璁惧鏍囪瘑')
    task_params: Mapped[Optional[dict]] = mapped_column(JSON, comment='浠诲姟鍙傛暟锛孞SON鏍煎紡')
    priority: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='浼樺厛绾э細0-鏅€?1-楂?2-绱ф€?)
    status: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='鐘舵€侊細0-寰呮墽琛?1-鎵ц涓?2-鎵ц鎴愬姛 3-鎵ц澶辫触 4-宸插彇娑?)
    retry_count: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='閲嶈瘯娆℃暟')
    max_retry_count: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'3'"), comment='鏈€澶ч噸璇曟鏁?)
    execute_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='璁″垝鎵ц鏃堕棿')
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='瀹為檯寮€濮嬫椂闂?)
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='瀹為檯缁撴潫鏃堕棿')
    result_message: Mapped[Optional[str]] = mapped_column(TEXT, comment='鎵ц缁撴灉淇℃伅')
    created_by: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='鍒涘缓鑰?)
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='鏇存柊鏃堕棿')


class MaintenanceTable(Base):
    __tablename__ = 'maintenance_table'
    __table_args__ = (
        Index('idx_machine_id', 'm_machine_id'),
        Index('idx_planned_time', 'm_planned_time'),
        Index('idx_status', 'm_status'),
        {'comment': '璁惧缁存姢琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='涓婚敭ID')
    m_machine_id: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='璁惧缂栧彿')
    m_maintenance_type: Mapped[Optional[int]] = mapped_column(TINYINT, comment='缁存姢绫诲瀷锛?-鏃ュ父锛?-鍛ㄥ父锛?-鏈堝父锛?-骞村害锛?)
    m_maintenance_content: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='缁存姢鍐呭')
    m_maintenance_person: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='缁存姢浜哄憳')
    m_planned_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='璁″垝鏃堕棿')
    m_actual_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='瀹為檯鏃堕棿')
    m_status: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='鐘舵€侊紙0-寰呮墽琛岋紝1-鎵ц涓紝2-宸插畬鎴愶級')
    m_remark: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='澶囨敞')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')


class ParamAlgorithm(Base):
    __tablename__ = 'param_algorithm'
    __table_args__ = (
        Index('idx_algorithm_name', 'algorithm_name'),
        Index('idx_created_time', 'created_time'),
        Index('idx_is_active', 'is_active'),
        {'comment': '绠楁硶鍙傛暟琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, server_default=text("'1'"), comment='涓婚敭ID锛屽浐瀹氫负1纭繚鍙湁涓€鏉¤褰?)
    s_PreProcess3DSPara: Mapped[dict] = mapped_column(JSON, nullable=False, comment='棰勫鐞嗗弬鏁?)
    s_DefectPlateBPara: Mapped[dict] = mapped_column(JSON, nullable=False, comment='缂洪櫡鍙傛暟')
    s_JggyPara: Mapped[dict] = mapped_column(JSON, nullable=False, comment='璺緞瑙勫垝鍙傛暟')
    algorithm_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='绠楁硶鍚嶇О')
    algorithm_version: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), server_default=text("'1.0'"), comment='绠楁硶鐗堟湰')
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='鍙傛暟鎻忚堪')
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'1'"), comment='鏄惁婵€娲伙紙1-婵€娲伙紝0-绂佺敤锛?)
    created_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='鍒涘缓浜?)
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')
    updated_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='鏇存柊浜?)
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='鏇存柊鏃堕棿')


class ParamMachine(Base):
    __tablename__ = 'param_machine'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_is_active', 'is_active'),
        Index('idx_setting_name', 'setting_name'),
        {'comment': '鏈哄彴鍙傛暟琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, server_default=text("'1'"), comment='涓婚敭ID锛屽浐瀹氫负1纭繚鍙湁涓€鏉¤褰?)
    s_BasicSettings: Mapped[Optional[dict]] = mapped_column(JSON, comment='鍩虹璁剧疆')
    s_PointSettings: Mapped[Optional[dict]] = mapped_column(JSON, comment='鐐逛綅璁剧疆')
    s_DeviceBehavior: Mapped[Optional[dict]] = mapped_column(JSON, comment='璁惧琛屼负')
    s_ToolParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='鍒€鍏峰弬鏁?)
    s_FixtureParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='澶瑰叿鍙傛暟')
    s_WorkpieceParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='宸ヤ欢鍙傛暟')
    s_ProcessParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='宸ヨ壓鍙傛暟')
    s_MachineInfo: Mapped[Optional[dict]] = mapped_column(JSON, comment='鏈哄彴淇℃伅')
    s_CameraParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='鐩告満鍙傛暟')
    s_DatabaseParameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='鏁版嵁搴撳弬鏁?)
    setting_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='閰嶇疆鍚嶇О')
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'), comment='閰嶇疆鎻忚堪')
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'1'"), comment='鏄惁婵€娲伙紙1-婵€娲伙紝0-绂佺敤锛?)
    created_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='鍒涘缓浜?)
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')
    updated_by: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='鏇存柊浜?)
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='鏇存柊鏃堕棿')


class ProcessHistory(Base):
    __tablename__ = 'process_history'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_task_id', 'ph_task_id'),
        Index('idx_workpiece_id', 'ph_workpiece_id'),
        {'comment': '宸ヨ壓鍙傛暟鍘嗗彶琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='涓婚敭ID')
    ph_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment='浠诲姟ID')
    ph_workpiece_id: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='宸ヤ欢ID')
    ph_parameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='宸ヨ壓鍙傛暟蹇収')
    ph_result: Mapped[Optional[dict]] = mapped_column(JSON, comment='鍔犲伐缁撴灉')
    ph_quality_score: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2), comment='璐ㄩ噺璇勫垎')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')


class QualityTable(Base):
    __tablename__ = 'quality_table'
    __table_args__ = (
        Index('idx_detection_time', 'q_detection_time'),
        Index('idx_qualify_status', 'q_qualify_status'),
        Index('idx_workpiece_id', 'q_workpiece_id'),
        {'comment': '璐ㄩ噺妫€娴嬭〃'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='涓婚敭ID')
    q_workpiece_id: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'), nullable=False, comment='宸ヤ欢缂栧彿')
    q_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment='浠诲姟ID')
    q_detection_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='妫€娴嬫椂闂?)
    q_roughness: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 3), comment='绮楃硻搴?)
    q_defect_count: Mapped[Optional[int]] = mapped_column(Integer, comment='缂洪櫡鏁伴噺')
    q_defect_details: Mapped[Optional[dict]] = mapped_column(JSON, comment='缂洪櫡璇︽儏')
    q_qualify_status: Mapped[Optional[int]] = mapped_column(TINYINT, comment='鍚堟牸鐘舵€侊紙0-涓嶅悎鏍硷紝1-鍚堟牸锛?)
    q_operator: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='妫€娴嬩汉鍛?)


class RecordTable(Base):
    __tablename__ = 'record_table'
    __table_args__ = (
        Index('idx_record_time', 'record_time'),
        Index('idx_record_workpiece', 'workpiece_id'),
        {'comment': '璁板綍琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='涓婚敭ID')
    workpiece_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('workpiece_table.id'),
        comment='鍏宠仈宸ヤ欢ID'
    )
    r_progress_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='杩涘害鏁版嵁')
    r_camera_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='鐩告満鏁版嵁')
    r_algorithm_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='绠楁硶鏁版嵁')
    r_machine_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='鏈哄彴鏁版嵁')
    r_warning_data: Mapped[Optional[dict]] = mapped_column(JSON, comment='璀﹀憡鏁版嵁')
    record_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='璁板綍鏃堕棿')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')


class StatusTable(Base):
    __tablename__ = 'status_table'
    __table_args__ = (
        CheckConstraint('(`id` = 1)', name='chk_single_row'),
        {'comment': '鐘舵€佺洃鎺ц〃锛堝崟璁板綍锛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, server_default=text("'1'"), comment='涓婚敭ID锛屽浐瀹氫负1纭繚鍙湁涓€鏉¤褰?)
    c_run_status: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='杩愯鐘舵€侊紙0-绌洪棽锛?-鍒濆鍖栧畬鎴愶紝2-杩愯锛?-鏆傚仠锛?-鍋滄锛?)
    c_alarm_status: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='鎶ヨ鐘舵€侊紙0-鏃犳姤璀︼紝1-鏈夋姤璀︼級')
    c_control_mode: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='鎺у埗鏂瑰紡锛?-鏈湴锛?-杩滅▼锛?)
    c_machine_mode: Mapped[int] = mapped_column(TINYINT, nullable=False, server_default=text("'0'"), comment='鏈哄彴妯″紡锛?-鎵嬪姩锛?-鑷姩锛?-鍗曟锛?-璋冭瘯锛?-缁存姢锛?)
    s_temperature: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2), comment='娓╁害')
    s_spindle_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='涓昏酱杞€?)
    s_feed_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='杩涚粰閫熷害')
    s_point_motion_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='鐐瑰姩閫熷害')
    s_tool_diameter: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='鍒€鍏风洿寰?)
    s_line_spacing: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='琛屽垁闂磋窛')
    s_total_cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='鍒囧墛鎬绘繁')
    s_clearance_speed: Mapped[Optional[int]] = mapped_column(Integer, comment='绌洪殭閫熷害')
    s_work_surface_height: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 2), comment='宸ヤ綔琛ㄩ潰楂樺害')
    s_cutting_depth: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2), comment='鍚冨垁娣卞害')
    s_step_distance: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 2), comment='姝ュ姩璺濈')
    f_fixture_status: Mapped[Optional[int]] = mapped_column(INTEGER, comment='澶瑰叿鐘舵€侊紙16浣嶄簩杩涘埗锛屾瘡浣嶄唬琛ㄤ竴涓す鍏风姸鎬侊級')
    p_absolute_position: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='缁濆鍧愭爣 "x,y,z"')
    p_relative_position: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='鐩稿鍧愭爣 "x,y,z"')
    p_work_position: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='宸ヤ綔鍧愭爣 "x,y,z"')
    p_remaining_distance: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='鍓╀綑璺濈 "x,y,z"')
    status_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鐘舵€佹椂闂?)
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='鏇存柊鏃堕棿')

class TaskTable(Base):
    __tablename__ = 'task_table'
    __table_args__ = (
        Index('idx_created_time', 'created_time'),
        Index('idx_status', 't_status'),
        Index('idx_task_workpiece', 't_workpiece_id'),
        Index('idx_task_record', 't_record_id'),
        {'comment': '任务管理表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='主键ID')
    t_task_name: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False, comment='任务名称')
    t_task_type: Mapped[int] = mapped_column(TINYINT, nullable=False, comment='任务类型（0-打磨，1-抛光，2-检测，3-维护）')
    t_workpiece_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='工件类型')
    t_material_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='材料类型')
    t_priority: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'1'"), comment='优先级')
    t_status: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='任务状态（0-待执行，1-执行中，2-已完成，3-暂停，4-取消）')
    t_progress: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2), server_default=text("'0.00'"), comment='进度百分比')
    t_estimated_time: Mapped[Optional[int]] = mapped_column(Integer, comment='预计耗时(分钟)')
    t_actual_time: Mapped[Optional[int]] = mapped_column(Integer, comment='实际耗时(分钟)')
    t_workpiece_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('workpiece_table.id'), comment='关联工件ID')
    t_record_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('record_table.id'), comment='关联记录ID')
    t_payload: Mapped[Optional[dict]] = mapped_column(JSON, comment='任务参数或控制指令')
    t_status_detail: Mapped[Optional[dict]] = mapped_column(JSON, comment='任务状态附加信息')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class WorkpieceTable(Base):
    __tablename__ = 'workpiece_table'
    __table_args__ = (
        Index('idx_status', 'w_status'),
        Index('idx_task_id', 'w_task_id'),
        Index('uk_workpiece_id', 'w_workpiece_id', unique=True),
        {'comment': '宸ヤ欢淇℃伅琛?}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='涓婚敭ID')
    w_workpiece_id: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'), nullable=False, comment='宸ヤ欢缂栧彿')
    w_workpiece_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='宸ヤ欢绫诲瀷')
    w_material: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'), comment='鏉愭枡')
    w_dimensions: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'), comment='灏哄 "闀?瀹?楂?')
    w_surface_requirement: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb4_unicode_ci'), comment='琛ㄩ潰瑕佹眰')
    w_roughness_required: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 3), comment='瑕佹眰绮楃硻搴?)
    w_roughness_actual: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 3), comment='瀹為檯绮楃硻搴?)
    w_status: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='鐘舵€侊紙0-寰呭姞宸ワ紝1-鍔犲伐涓紝2-宸插畬鎴愶紝3-涓嶅悎鏍硷級')
    w_task_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment='鍏宠仈浠诲姟ID')
    created_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='鍒涘缓鏃堕棿')
