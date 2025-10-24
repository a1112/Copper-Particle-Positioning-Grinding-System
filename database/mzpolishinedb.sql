/*
 Navicat Premium Dump SQL

 Source Server         : 192.168.1.214
 Source Server Type    : MySQL
 Source Server Version : 80037 (8.0.37)
 Source Host           : 192.168.1.214:3306
 Source Schema         : mzpolishinedb

 Target Server Type    : MySQL
 Target Server Version : 80037 (8.0.37)
 File Encoding         : 65001

 Date: 24/10/2025 16:41:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for action_table
-- ----------------------------
DROP TABLE IF EXISTS `action_table`;
CREATE TABLE `action_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `action_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '动作名称',
  `command` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '指令',
  `status` tinyint NOT NULL DEFAULT 0 COMMENT '状态（0-待执行，1-执行中，2-已完成，3-失败）',
  `priority` tinyint NULL DEFAULT 1 COMMENT '优先级（1-低，2-中，3-高）',
  `execute_times` int NULL DEFAULT 0 COMMENT '执行次数',
  `max_retries` int NULL DEFAULT 3 COMMENT '最大重试次数',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '错误信息',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_priority`(`priority` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '动作表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of action_table
-- ----------------------------

-- ----------------------------
-- Table structure for hardware_task_queue
-- ----------------------------
DROP TABLE IF EXISTS `hardware_task_queue`;
CREATE TABLE `hardware_task_queue`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '任务唯一标识',
  `task_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '任务类型：POLISH_START/ POLISH_STOP/ TEMPERATURE_SET/ PRESSURE_ADJUST等',
  `device_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备标识',
  `task_params` json NULL COMMENT '任务参数，JSON格式',
  `priority` tinyint NULL DEFAULT 0 COMMENT '优先级：0-普通 1-高 2-紧急',
  `status` tinyint NULL DEFAULT 0 COMMENT '状态：0-待执行 1-执行中 2-执行成功 3-执行失败 4-已取消',
  `retry_count` tinyint NULL DEFAULT 0 COMMENT '重试次数',
  `max_retry_count` tinyint NULL DEFAULT 3 COMMENT '最大重试次数',
  `execute_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '计划执行时间',
  `start_time` datetime NULL DEFAULT NULL COMMENT '实际开始时间',
  `end_time` datetime NULL DEFAULT NULL COMMENT '实际结束时间',
  `result_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '执行结果信息',
  `created_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '创建者',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `task_id`(`task_id` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_device_status`(`device_id` ASC, `status` ASC) USING BTREE,
  INDEX `idx_execute_time`(`execute_time` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '硬件控制任务轮询表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of hardware_task_queue
-- ----------------------------

-- ----------------------------
-- Table structure for maintenance_table
-- ----------------------------
DROP TABLE IF EXISTS `maintenance_table`;
CREATE TABLE `maintenance_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `m_machine_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '设备编号',
  `m_maintenance_type` tinyint NULL DEFAULT NULL COMMENT '维护类型（0-日常，1-周常，2-月常，3-年度）',
  `m_maintenance_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '维护内容',
  `m_maintenance_person` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '维护人员',
  `m_planned_time` datetime NULL DEFAULT NULL COMMENT '计划时间',
  `m_actual_time` datetime NULL DEFAULT NULL COMMENT '实际时间',
  `m_status` tinyint NULL DEFAULT 0 COMMENT '状态（0-待执行，1-执行中，2-已完成）',
  `m_remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '备注',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_machine_id`(`m_machine_id` ASC) USING BTREE,
  INDEX `idx_planned_time`(`m_planned_time` ASC) USING BTREE,
  INDEX `idx_status`(`m_status` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '设备维护表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of maintenance_table
-- ----------------------------

-- ----------------------------
-- Table structure for param_algorithm
-- ----------------------------
DROP TABLE IF EXISTS `param_algorithm`;
CREATE TABLE `param_algorithm`  (
  `id` bigint NOT NULL DEFAULT 1 COMMENT '主键ID，固定为1确保只有一条记录',
  `s_PreProcess3DSPara` json NOT NULL COMMENT '预处理参数',
  `s_DefectPlateBPara` json NOT NULL COMMENT '缺陷参数',
  `s_JggyPara` json NOT NULL COMMENT '路径规划参数',
  `algorithm_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '算法名称',
  `algorithm_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '1.0' COMMENT '算法版本',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '参数描述',
  `is_active` tinyint NULL DEFAULT 1 COMMENT '是否激活（1-激活，0-禁用）',
  `created_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '创建人',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '更新人',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_algorithm_name`(`algorithm_name` ASC) USING BTREE,
  INDEX `idx_is_active`(`is_active` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '算法参数表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of param_algorithm
-- ----------------------------

-- ----------------------------
-- Table structure for param_machine
-- ----------------------------
DROP TABLE IF EXISTS `param_machine`;
CREATE TABLE `param_machine`  (
  `id` bigint NOT NULL DEFAULT 1 COMMENT '主键ID，固定为1确保只有一条记录',
  `s_BasicSettings` json NULL COMMENT '基础设置',
  `s_PointSettings` json NULL COMMENT '点位设置',
  `s_DeviceBehavior` json NULL COMMENT '设备行为',
  `s_ToolParameters` json NULL COMMENT '刀具参数',
  `s_FixtureParameters` json NULL COMMENT '夹具参数',
  `s_WorkpieceParameters` json NULL COMMENT '工件参数',
  `s_ProcessParameters` json NULL COMMENT '工艺参数',
  `s_MachineInfo` json NULL COMMENT '机台信息',
  `s_CameraParameters` json NULL COMMENT '相机参数',
  `s_DatabaseParameters` json NULL COMMENT '数据库参数',
  `setting_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '配置名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '配置描述',
  `is_active` tinyint NULL DEFAULT 1 COMMENT '是否激活（1-激活，0-禁用）',
  `created_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '创建人',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '更新人',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_setting_name`(`setting_name` ASC) USING BTREE,
  INDEX `idx_is_active`(`is_active` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '机台参数表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of param_machine
-- ----------------------------

-- ----------------------------
-- Table structure for process_history
-- ----------------------------
DROP TABLE IF EXISTS `process_history`;
CREATE TABLE `process_history`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ph_task_id` bigint NULL DEFAULT NULL COMMENT '任务ID',
  `ph_workpiece_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '工件ID',
  `ph_parameters` json NULL COMMENT '工艺参数快照',
  `ph_result` json NULL COMMENT '加工结果',
  `ph_quality_score` decimal(5, 2) NULL DEFAULT NULL COMMENT '质量评分',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_task_id`(`ph_task_id` ASC) USING BTREE,
  INDEX `idx_workpiece_id`(`ph_workpiece_id` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '工艺参数历史表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of process_history
-- ----------------------------

-- ----------------------------
-- Table structure for quality_table
-- ----------------------------
DROP TABLE IF EXISTS `quality_table`;
CREATE TABLE `quality_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `q_workpiece_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '工件编号',
  `q_task_id` bigint NULL DEFAULT NULL COMMENT '任务ID',
  `q_detection_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '检测时间',
  `q_roughness` decimal(5, 3) NULL DEFAULT NULL COMMENT '粗糙度',
  `q_defect_count` int NULL DEFAULT NULL COMMENT '缺陷数量',
  `q_defect_details` json NULL COMMENT '缺陷详情',
  `q_qualify_status` tinyint NULL DEFAULT NULL COMMENT '合格状态（0-不合格，1-合格）',
  `q_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '检测人员',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_workpiece_id`(`q_workpiece_id` ASC) USING BTREE,
  INDEX `idx_detection_time`(`q_detection_time` ASC) USING BTREE,
  INDEX `idx_qualify_status`(`q_qualify_status` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '质量检测表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of quality_table
-- ----------------------------

-- ----------------------------
-- Table structure for record_table
-- ----------------------------
DROP TABLE IF EXISTS `record_table`;
CREATE TABLE `record_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `r_progress_data` json NULL COMMENT '进度数据',
  `r_camera_data` json NULL COMMENT '相机数据',
  `r_algorithm_data` json NULL COMMENT '算法数据',
  `r_machine_data` json NULL COMMENT '机台数据',
  `r_warning_data` json NULL COMMENT '警告数据',
  `record_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_record_time`(`record_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of record_table
-- ----------------------------

-- ----------------------------
-- Table structure for status_table
-- ----------------------------
DROP TABLE IF EXISTS `status_table`;
CREATE TABLE `status_table`  (
  `id` bigint NOT NULL DEFAULT 1 COMMENT '主键ID，固定为1确保只有一条记录',
  `c_run_status` tinyint NOT NULL DEFAULT 0 COMMENT '运行状态（0-空闲，1-初始化完成，2-运行，3-暂停，4-停止）',
  `c_alarm_status` tinyint NOT NULL DEFAULT 0 COMMENT '报警状态（0-无报警，1-有报警）',
  `c_control_mode` tinyint NOT NULL DEFAULT 0 COMMENT '控制方式（0-本地，1-远程）',
  `c_machine_mode` tinyint NOT NULL DEFAULT 0 COMMENT '机台模式（0-手动，1-自动，2-单步，3-调试，4-维护）',
  `s_temperature` decimal(5, 2) NULL DEFAULT NULL COMMENT '温度',
  `s_spindle_speed` int NULL DEFAULT NULL COMMENT '主轴转速',
  `s_feed_speed` int NULL DEFAULT NULL COMMENT '进给速度',
  `s_point_motion_speed` int NULL DEFAULT NULL COMMENT '点动速度',
  `s_tool_diameter` decimal(6, 2) NULL DEFAULT NULL COMMENT '刀具直径',
  `s_line_spacing` decimal(6, 2) NULL DEFAULT NULL COMMENT '行刀间距',
  `s_total_cutting_depth` decimal(6, 2) NULL DEFAULT NULL COMMENT '切削总深',
  `s_clearance_speed` int NULL DEFAULT NULL COMMENT '空隙速度',
  `s_work_surface_height` decimal(8, 2) NULL DEFAULT NULL COMMENT '工作表面高度',
  `s_cutting_depth` decimal(6, 2) NULL DEFAULT NULL COMMENT '吃刀深度',
  `s_step_distance` decimal(8, 2) NULL DEFAULT NULL COMMENT '步动距离',
  `f_fixture_status` int UNSIGNED NULL DEFAULT NULL COMMENT '夹具状态（16位二进制，每位代表一个夹具状态）',
  `p_absolute_position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '绝对坐标 \"x,y,z\"',
  `p_relative_position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '相对坐标 \"x,y,z\"',
  `p_work_position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '工作坐标 \"x,y,z\"',
  `p_remaining_distance` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '剩余距离 \"x,y,z\"',
  `status_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '状态时间',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `chk_single_row` CHECK (`id` = 1)
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '状态监控表（单记录）' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of status_table
-- ----------------------------
INSERT INTO `status_table` VALUES (1, 2, 0, 1, 1, 29.33, 2418, 134, 673, 6.00, 2.50, 10.00, 800, 50.00, 1.00, 0.50, 11, '105.032,203.908,52.1848', '95.0322,193.908,47.1848', '105.032,203.908,52.1848', '394.968,296.092,47.8152', '2025-10-24 16:41:22', '2025-10-24 16:41:21', '2025-10-24 16:41:21');

-- ----------------------------
-- Table structure for task_table
-- ----------------------------
DROP TABLE IF EXISTS `task_table`;
CREATE TABLE `task_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `t_task_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '任务名称',
  `t_task_type` tinyint NOT NULL COMMENT '任务类型（0-打磨，1-抛光，2-检测，3-维护）',
  `t_workpiece_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '工件类型',
  `t_material_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '材料类型',
  `t_priority` tinyint NULL DEFAULT 1 COMMENT '优先级',
  `t_status` tinyint NULL DEFAULT 0 COMMENT '任务状态（0-待执行，1-执行中，2-已完成，3-暂停，4-取消）',
  `t_progress` decimal(5, 2) NULL DEFAULT 0.00 COMMENT '进度百分比',
  `t_estimated_time` int NULL DEFAULT NULL COMMENT '预计耗时(秒)',
  `t_actual_time` int NULL DEFAULT NULL COMMENT '实际耗时(秒)',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_status`(`t_status` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '任务管理表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of task_table
-- ----------------------------

-- ----------------------------
-- Table structure for workpiece_table
-- ----------------------------
DROP TABLE IF EXISTS `workpiece_table`;
CREATE TABLE `workpiece_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `w_workpiece_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '工件编号',
  `w_workpiece_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '工件类型',
  `w_material` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '材料',
  `w_dimensions` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '尺寸 \"长,宽,高\"',
  `w_surface_requirement` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '表面要求',
  `w_roughness_required` decimal(5, 3) NULL DEFAULT NULL COMMENT '要求粗糙度',
  `w_roughness_actual` decimal(5, 3) NULL DEFAULT NULL COMMENT '实际粗糙度',
  `w_status` tinyint NULL DEFAULT 0 COMMENT '状态（0-待加工，1-加工中，2-已完成，3-不合格）',
  `w_task_id` bigint NULL DEFAULT NULL COMMENT '关联任务ID',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_workpiece_id`(`w_workpiece_id` ASC) USING BTREE,
  INDEX `idx_status`(`w_status` ASC) USING BTREE,
  INDEX `idx_task_id`(`w_task_id` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '工件信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of workpiece_table
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
