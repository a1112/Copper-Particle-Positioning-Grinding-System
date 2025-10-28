-- 算法参数表
CREATE TABLE param_algorithm (
    id BIGINT PRIMARY KEY DEFAULT 1 COMMENT '主键ID，固定为1确保只有一条记录',
    
    -- 核心参数字段
    s_PreProcess3DSPara JSON NOT NULL COMMENT '预处理参数',
    s_DefectPlateBPara JSON NOT NULL COMMENT '缺陷参数', 
    s_JggyPara JSON NOT NULL COMMENT '路径规划参数',
    
    -- 管理字段
    algorithm_name VARCHAR(100) COMMENT '算法名称',
    algorithm_version VARCHAR(50) DEFAULT '1.0' COMMENT '算法版本',
    description TEXT COMMENT '参数描述',
    is_active TINYINT DEFAULT 1 COMMENT '是否激活（1-激活，0-禁用）',
    created_by VARCHAR(100) COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by VARCHAR(100) COMMENT '更新人',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_algorithm_name (algorithm_name),
    INDEX idx_is_active (is_active),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='算法参数表';

-- 机台参数表
CREATE TABLE param_machine (
    id BIGINT PRIMARY KEY DEFAULT 1 COMMENT '主键ID，固定为1确保只有一条记录',
    
    -- 所有JSON参数字段统一命名样式
    s_BasicSettings JSON COMMENT '基础设置',
    s_PointSettings JSON COMMENT '点位设置',
    s_DeviceBehavior JSON COMMENT '设备行为',
    s_ToolParameters JSON COMMENT '刀具参数',
    s_FixtureParameters JSON COMMENT '夹具参数',
    s_WorkpieceParameters JSON COMMENT '工件参数',
    s_ProcessParameters JSON COMMENT '工艺参数',
    s_MachineInfo JSON COMMENT '机台信息',
    s_CameraParameters JSON COMMENT '相机参数',
    s_DatabaseParameters JSON COMMENT '数据库参数',
    
    -- 管理字段
    setting_name VARCHAR(100) COMMENT '配置名称',
    description TEXT COMMENT '配置描述',
    is_active TINYINT DEFAULT 1 COMMENT '是否激活（1-激活，0-禁用）',
    created_by VARCHAR(100) COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by VARCHAR(100) COMMENT '更新人',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_setting_name (setting_name),
    INDEX idx_is_active (is_active),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='机台参数表';


-- 状态表 - 只保留一条记录
CREATE TABLE status_table (
    id BIGINT PRIMARY KEY DEFAULT 1 COMMENT '主键ID，固定为1确保只有一条记录',
    
    -- 核心状态字段（统一c_前缀）
    c_run_status TINYINT NOT NULL DEFAULT 0 COMMENT '运行状态（0-空闲，1-初始化完成，2-运行，3-暂停，4-停止）',
    c_alarm_status TINYINT NOT NULL DEFAULT 0 COMMENT '报警状态（0-无报警，1-有报警）',
    c_control_mode TINYINT NOT NULL DEFAULT 0 COMMENT '控制方式（0-本地，1-远程）',
    c_machine_mode TINYINT NOT NULL DEFAULT 0 COMMENT '机台模式（0-手动，1-自动，2-单步，3-调试，4-维护）',
		
		-- 连接状态字段
    c_camera_connected TINYINT NOT NULL DEFAULT 0 COMMENT '相机连接状态（0-未连接，1-已连接）',
    c_device_connected TINYINT NOT NULL DEFAULT 0 COMMENT '机台设备连接状态（0-未连接，1-已连接）',
    
    -- 主轴加工参数（统一s_前缀）
    s_temperature DECIMAL(5,2) COMMENT '温度',
    s_spindle_speed INT COMMENT '主轴转速',
    s_feed_speed INT COMMENT '进给速度',
    s_point_motion_speed INT COMMENT '点动速度',
    s_tool_diameter DECIMAL(6,2) COMMENT '刀具直径',
    s_line_spacing DECIMAL(6,2) COMMENT '行刀间距',
    s_total_cutting_depth DECIMAL(6,2) COMMENT '切削总深',
    s_clearance_speed INT COMMENT '空隙速度',
    s_work_surface_height DECIMAL(8,2) COMMENT '工作表面高度',
    s_cutting_depth DECIMAL(6,2) COMMENT '吃刀深度',
    s_step_distance DECIMAL(8,2) COMMENT '步动距离',
    -- 夹具状态（统一f_前缀）
    f_fixture_status VARCHAR(255) COMMENT '夹具状态',
    -- 坐标位置数据（统一p_前缀）
    p_absolute_position VARCHAR(100) COMMENT '绝对坐标 "x,y,z"',
    p_relative_position VARCHAR(100) COMMENT '相对坐标 "x,y,z"',
    p_work_position VARCHAR(100) COMMENT '工作坐标 "x,y,z"',
    p_remaining_distance VARCHAR(100) COMMENT '剩余距离 "x,y,z"',
    
    -- 时间字段
    status_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '状态时间',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 约束确保只有一条记录
    CONSTRAINT chk_single_row CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='状态监控表（单记录）';

CREATE TABLE record_table (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    
    -- 记录数据（统一r_前缀）
    r_progress_data JSON COMMENT '进度数据',
    r_camera_data JSON COMMENT '相机数据',
    r_algorithm_data JSON COMMENT '算法数据',
    r_machine_data JSON COMMENT '机台数据',
    r_warning_data JSON COMMENT '警告数据',
    
    -- 时间字段
    record_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 索引优化
    INDEX idx_record_time (record_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='记录表';

CREATE TABLE `hardware_task_queue`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_name` varchar(64) NOT NULL COMMENT '任务名称',
  `task_type` int NOT NULL COMMENT '任务类型：1-开始抛光, 2-停止抛光, 3-温度设置, 4-压力调整等',
  `device_id` int NOT NULL COMMENT '设备标识ID',
  `task_params` json COMMENT '任务参数，JSON格式',
  `priority` int DEFAULT 0 COMMENT '优先级：0-普通 1-高 2-紧急',
  `status` int DEFAULT 0 COMMENT '状态：0-待执行 1-执行中 2-执行成功 3-执行失败 4-已取消',
	`status_params` json COMMENT '任务状态，JSON格式',
  `retry_count` int DEFAULT 0 COMMENT '重试次数',
  `max_retry_count` int DEFAULT 3 COMMENT '最大重试次数',
  `execute_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '计划执行时间',
  `start_time` datetime DEFAULT NULL COMMENT '实际开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '实际结束时间',
  `result_message` text COMMENT '执行结果信息',
  `created_by` varchar(50) DEFAULT NULL COMMENT '创建者',
  `created_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_status`(`status`),
  INDEX `idx_device_status`(`device_id`, `status`),
  INDEX `idx_execute_time`(`execute_time`),
  INDEX `idx_created_time`(`created_time`)
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '硬件控制任务轮询表';
