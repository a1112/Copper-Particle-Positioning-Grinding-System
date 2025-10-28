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
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '涓婚敭ID',
  `action_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '鍔ㄤ綔鍚嶇О',
  `command` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '鎸囦护',
  `status` tinyint NOT NULL DEFAULT 0 COMMENT '鐘舵€侊紙0-寰呮墽琛岋紝1-鎵ц涓紝2-宸插畬鎴愶紝3-澶辫触锛?,
  `priority` tinyint NULL DEFAULT 1 COMMENT '浼樺厛绾э紙1-浣庯紝2-涓紝3-楂橈級',
  `execute_times` int NULL DEFAULT 0 COMMENT '鎵ц娆℃暟',
  `max_retries` int NULL DEFAULT 3 COMMENT '鏈€澶ч噸璇曟鏁?,
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '閿欒淇℃伅',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '鏇存柊鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_priority`(`priority` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '鍔ㄤ綔琛? ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of action_table
-- ----------------------------

-- ----------------------------
-- Table structure for hardware_task_queue
-- ----------------------------
DROP TABLE IF EXISTS `hardware_task_queue`;
CREATE TABLE `hardware_task_queue`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '涓婚敭ID',
  `task_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '浠诲姟鍞竴鏍囪瘑',
  `task_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '浠诲姟绫诲瀷锛歅OLISH_START/ POLISH_STOP/ TEMPERATURE_SET/ PRESSURE_ADJUST绛?,
  `device_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '璁惧鏍囪瘑',
  `task_params` json NULL COMMENT '浠诲姟鍙傛暟锛孞SON鏍煎紡',
  `priority` tinyint NULL DEFAULT 0 COMMENT '浼樺厛绾э細0-鏅€?1-楂?2-绱ф€?,
  `status` tinyint NULL DEFAULT 0 COMMENT '鐘舵€侊細0-寰呮墽琛?1-鎵ц涓?2-鎵ц鎴愬姛 3-鎵ц澶辫触 4-宸插彇娑?,
  `retry_count` tinyint NULL DEFAULT 0 COMMENT '閲嶈瘯娆℃暟',
  `max_retry_count` tinyint NULL DEFAULT 3 COMMENT '鏈€澶ч噸璇曟鏁?,
  `execute_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '璁″垝鎵ц鏃堕棿',
  `start_time` datetime NULL DEFAULT NULL COMMENT '瀹為檯寮€濮嬫椂闂?,
  `end_time` datetime NULL DEFAULT NULL COMMENT '瀹為檯缁撴潫鏃堕棿',
  `result_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '鎵ц缁撴灉淇℃伅',
  `created_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '鍒涘缓鑰?,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '鏇存柊鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `task_id`(`task_id` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_device_status`(`device_id` ASC, `status` ASC) USING BTREE,
  INDEX `idx_execute_time`(`execute_time` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '纭欢鎺у埗浠诲姟杞琛? ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of hardware_task_queue
-- ----------------------------

-- ----------------------------
-- Table structure for maintenance_table
-- ----------------------------
DROP TABLE IF EXISTS `maintenance_table`;
CREATE TABLE `maintenance_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '涓婚敭ID',
  `m_machine_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '璁惧缂栧彿',
  `m_maintenance_type` tinyint NULL DEFAULT NULL COMMENT '缁存姢绫诲瀷锛?-鏃ュ父锛?-鍛ㄥ父锛?-鏈堝父锛?-骞村害锛?,
  `m_maintenance_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '缁存姢鍐呭',
  `m_maintenance_person` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '缁存姢浜哄憳',
  `m_planned_time` datetime NULL DEFAULT NULL COMMENT '璁″垝鏃堕棿',
  `m_actual_time` datetime NULL DEFAULT NULL COMMENT '瀹為檯鏃堕棿',
  `m_status` tinyint NULL DEFAULT 0 COMMENT '鐘舵€侊紙0-寰呮墽琛岋紝1-鎵ц涓紝2-宸插畬鎴愶級',
  `m_remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '澶囨敞',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_machine_id`(`m_machine_id` ASC) USING BTREE,
  INDEX `idx_planned_time`(`m_planned_time` ASC) USING BTREE,
  INDEX `idx_status`(`m_status` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '璁惧缁存姢琛? ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of maintenance_table
-- ----------------------------

-- ----------------------------
-- Table structure for param_algorithm
-- ----------------------------
DROP TABLE IF EXISTS `param_algorithm`;
CREATE TABLE `param_algorithm`  (
  `id` bigint NOT NULL DEFAULT 1 COMMENT '涓婚敭ID锛屽浐瀹氫负1纭繚鍙湁涓€鏉¤褰?,
  `s_PreProcess3DSPara` json NOT NULL COMMENT '棰勫鐞嗗弬鏁?,
  `s_DefectPlateBPara` json NOT NULL COMMENT '缂洪櫡鍙傛暟',
  `s_JggyPara` json NOT NULL COMMENT '璺緞瑙勫垝鍙傛暟',
  `algorithm_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '绠楁硶鍚嶇О',
  `algorithm_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '1.0' COMMENT '绠楁硶鐗堟湰',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '鍙傛暟鎻忚堪',
  `is_active` tinyint NULL DEFAULT 1 COMMENT '鏄惁婵€娲伙紙1-婵€娲伙紝0-绂佺敤锛?,
  `created_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '鍒涘缓浜?,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  `updated_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '鏇存柊浜?,
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '鏇存柊鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_algorithm_name`(`algorithm_name` ASC) USING BTREE,
  INDEX `idx_is_active`(`is_active` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '绠楁硶鍙傛暟琛? ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of param_algorithm
-- ----------------------------

-- ----------------------------
-- Table structure for param_machine
-- ----------------------------
DROP TABLE IF EXISTS `param_machine`;
CREATE TABLE `param_machine`  (
  `id` bigint NOT NULL DEFAULT 1 COMMENT '涓婚敭ID锛屽浐瀹氫负1纭繚鍙湁涓€鏉¤褰?,
  `s_BasicSettings` json NULL COMMENT '鍩虹璁剧疆',
  `s_PointSettings` json NULL COMMENT '鐐逛綅璁剧疆',
  `s_DeviceBehavior` json NULL COMMENT '璁惧琛屼负',
  `s_ToolParameters` json NULL COMMENT '鍒€鍏峰弬鏁?,
  `s_FixtureParameters` json NULL COMMENT '澶瑰叿鍙傛暟',
  `s_WorkpieceParameters` json NULL COMMENT '宸ヤ欢鍙傛暟',
  `s_ProcessParameters` json NULL COMMENT '宸ヨ壓鍙傛暟',
  `s_MachineInfo` json NULL COMMENT '鏈哄彴淇℃伅',
  `s_CameraParameters` json NULL COMMENT '鐩告満鍙傛暟',
  `s_DatabaseParameters` json NULL COMMENT '鏁版嵁搴撳弬鏁?,
  `setting_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '閰嶇疆鍚嶇О',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '閰嶇疆鎻忚堪',
  `is_active` tinyint NULL DEFAULT 1 COMMENT '鏄惁婵€娲伙紙1-婵€娲伙紝0-绂佺敤锛?,
  `created_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '鍒涘缓浜?,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  `updated_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '鏇存柊浜?,
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '鏇存柊鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_setting_name`(`setting_name` ASC) USING BTREE,
  INDEX `idx_is_active`(`is_active` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '鏈哄彴鍙傛暟琛? ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of param_machine
-- ----------------------------

-- ----------------------------
-- Table structure for process_history
-- ----------------------------
DROP TABLE IF EXISTS `process_history`;
CREATE TABLE `process_history`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '涓婚敭ID',
  `ph_task_id` bigint NULL DEFAULT NULL COMMENT '浠诲姟ID',
  `ph_workpiece_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '宸ヤ欢ID',
  `ph_parameters` json NULL COMMENT '宸ヨ壓鍙傛暟蹇収',
  `ph_result` json NULL COMMENT '鍔犲伐缁撴灉',
  `ph_quality_score` decimal(5, 2) NULL DEFAULT NULL COMMENT '璐ㄩ噺璇勫垎',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_task_id`(`ph_task_id` ASC) USING BTREE,
  INDEX `idx_workpiece_id`(`ph_workpiece_id` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '宸ヨ壓鍙傛暟鍘嗗彶琛? ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of process_history
-- ----------------------------

-- ----------------------------
-- Table structure for quality_table
-- ----------------------------
DROP TABLE IF EXISTS `quality_table`;
CREATE TABLE `quality_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '涓婚敭ID',
  `q_workpiece_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '宸ヤ欢缂栧彿',
  `q_task_id` bigint NULL DEFAULT NULL COMMENT '浠诲姟ID',
  `q_detection_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '妫€娴嬫椂闂?,
  `q_roughness` decimal(5, 3) NULL DEFAULT NULL COMMENT '绮楃硻搴?,
  `q_defect_count` int NULL DEFAULT NULL COMMENT '缂洪櫡鏁伴噺',
  `q_defect_details` json NULL COMMENT '缂洪櫡璇︽儏',
  `q_qualify_status` tinyint NULL DEFAULT NULL COMMENT '鍚堟牸鐘舵€侊紙0-涓嶅悎鏍硷紝1-鍚堟牸锛?,
  `q_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '妫€娴嬩汉鍛?,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_workpiece_id`(`q_workpiece_id` ASC) USING BTREE,
  INDEX `idx_detection_time`(`q_detection_time` ASC) USING BTREE,
  INDEX `idx_qualify_status`(`q_qualify_status` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '璐ㄩ噺妫€娴嬭〃' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of quality_table
-- ----------------------------

-- ----------------------------
-- Table structure for record_table
-- ----------------------------
DROP TABLE IF EXISTS `record_table`;
CREATE TABLE `record_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '涓婚敭ID',
  `workpiece_id` bigint NULL DEFAULT NULL COMMENT '鍏宠仈宸ヤ欢ID',
  `r_progress_data` json NULL COMMENT '杩涘害鏁版嵁',
  `r_camera_data` json NULL COMMENT '鐩告満鏁版嵁',
  `r_algorithm_data` json NULL COMMENT '绠楁硶鏁版嵁',
  `r_machine_data` json NULL COMMENT '鏈哄彴鏁版嵁',
  `r_warning_data` json NULL COMMENT '璀﹀憡鏁版嵁',
  `record_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '璁板綍鏃堕棿',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_record_time`(`record_time` ASC) USING BTREE,
  INDEX `idx_record_workpiece`(`workpiece_id` ASC) USING BTREE,
  CONSTRAINT `fk_record_workpiece` FOREIGN KEY (`workpiece_id`) REFERENCES `workpiece_table` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '璁板綍琛? ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of record_table
-- ----------------------------

-- ----------------------------
-- Table structure for alarm_table
-- ----------------------------
DROP TABLE IF EXISTS `alarm_table`;
CREATE TABLE `alarm_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `record_id` bigint NOT NULL COMMENT '关联记录ID',
  `alarm_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '报警类型',
  `alarm_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '报警代码',
  `alarm_message` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '报警信息',
  `alarm_level` tinyint NOT NULL DEFAULT 0 COMMENT '报警等级',
  `handled_status` tinyint NOT NULL DEFAULT 0 COMMENT '处理状态（0-未处理，1-处理中，2-已处理）',
  `alarm_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报警时间',
  `handled_time` datetime NULL DEFAULT NULL COMMENT '处理时间',
  `handler` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '处理人',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_record_id`(`record_id` ASC) USING BTREE,
  INDEX `idx_alarm_level`(`alarm_level` ASC) USING BTREE,
  CONSTRAINT `fk_alarm_record` FOREIGN KEY (`record_id`) REFERENCES `record_table` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '报警信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alarm_table
-- ----------------------------

-- ----------------------------
-- Table structure for status_table
-- ----------------------------
DROP TABLE IF EXISTS `status_table`;
CREATE TABLE `status_table`  (
  `id` bigint NOT NULL DEFAULT 1 COMMENT '涓婚敭ID锛屽浐瀹氫负1纭繚鍙湁涓€鏉¤褰?,
  `c_run_status` tinyint NOT NULL DEFAULT 0 COMMENT '杩愯鐘舵€侊紙0-绌洪棽锛?-鍒濆鍖栧畬鎴愶紝2-杩愯锛?-鏆傚仠锛?-鍋滄锛?,
  `c_alarm_status` tinyint NOT NULL DEFAULT 0 COMMENT '鎶ヨ鐘舵€侊紙0-鏃犳姤璀︼紝1-鏈夋姤璀︼級',
  `c_control_mode` tinyint NOT NULL DEFAULT 0 COMMENT '鎺у埗鏂瑰紡锛?-鏈湴锛?-杩滅▼锛?,
  `c_machine_mode` tinyint NOT NULL DEFAULT 0 COMMENT '鏈哄彴妯″紡锛?-鎵嬪姩锛?-鑷姩锛?-鍗曟锛?-璋冭瘯锛?-缁存姢锛?,
  `s_temperature` decimal(5, 2) NULL DEFAULT NULL COMMENT '娓╁害',
  `s_spindle_speed` int NULL DEFAULT NULL COMMENT '涓昏酱杞€?,
  `s_feed_speed` int NULL DEFAULT NULL COMMENT '杩涚粰閫熷害',
  `s_point_motion_speed` int NULL DEFAULT NULL COMMENT '鐐瑰姩閫熷害',
  `s_tool_diameter` decimal(6, 2) NULL DEFAULT NULL COMMENT '鍒€鍏风洿寰?,
  `s_line_spacing` decimal(6, 2) NULL DEFAULT NULL COMMENT '琛屽垁闂磋窛',
  `s_total_cutting_depth` decimal(6, 2) NULL DEFAULT NULL COMMENT '鍒囧墛鎬绘繁',
  `s_clearance_speed` int NULL DEFAULT NULL COMMENT '绌洪殭閫熷害',
  `s_work_surface_height` decimal(8, 2) NULL DEFAULT NULL COMMENT '宸ヤ綔琛ㄩ潰楂樺害',
  `s_cutting_depth` decimal(6, 2) NULL DEFAULT NULL COMMENT '鍚冨垁娣卞害',
  `s_step_distance` decimal(8, 2) NULL DEFAULT NULL COMMENT '姝ュ姩璺濈',
  `f_fixture_status` int UNSIGNED NULL DEFAULT NULL COMMENT '澶瑰叿鐘舵€侊紙16浣嶄簩杩涘埗锛屾瘡浣嶄唬琛ㄤ竴涓す鍏风姸鎬侊級',
  `p_absolute_position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '缁濆鍧愭爣 \"x,y,z\"',
  `p_relative_position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '鐩稿鍧愭爣 \"x,y,z\"',
  `p_work_position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '宸ヤ綔鍧愭爣 \"x,y,z\"',
  `p_remaining_distance` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '鍓╀綑璺濈 \"x,y,z\"',
  `status_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鐘舵€佹椂闂?,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '鏇存柊鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `chk_single_row` CHECK (`id` = 1)
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '鐘舵€佺洃鎺ц〃锛堝崟璁板綍锛? ROW_FORMAT = Dynamic;

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
  `t_estimated_time` int NULL DEFAULT NULL COMMENT '预计耗时(分钟)',
  `t_actual_time` int NULL DEFAULT NULL COMMENT '实际耗时(分钟)',
  `t_workpiece_id` bigint NULL DEFAULT NULL COMMENT '关联工件ID',
  `t_record_id` bigint NULL DEFAULT NULL COMMENT '关联记录ID',
  `t_payload` json NULL COMMENT '任务参数或控制指令',
  `t_status_detail` json NULL COMMENT '任务状态附加信息',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_status`(`t_status` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE,
  INDEX `idx_task_workpiece`(`t_workpiece_id` ASC) USING BTREE,
  INDEX `idx_task_record`(`t_record_id` ASC) USING BTREE,
  CONSTRAINT `fk_task_workpiece` FOREIGN KEY (`t_workpiece_id`) REFERENCES `workpiece_table` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_task_record` FOREIGN KEY (`t_record_id`) REFERENCES `record_table` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '任务管理表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of task_table
-- ----------------------------

-- ----------------------------
-- Table structure for workpiece_table
-- ----------------------------
DROP TABLE IF EXISTS `workpiece_table`;
CREATE TABLE `workpiece_table`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '涓婚敭ID',
  `w_workpiece_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '宸ヤ欢缂栧彿',
  `w_workpiece_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '宸ヤ欢绫诲瀷',
  `w_material` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '鏉愭枡',
  `w_dimensions` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '灏哄 \"闀?瀹?楂榎"',
  `w_surface_requirement` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '琛ㄩ潰瑕佹眰',
  `w_roughness_required` decimal(5, 3) NULL DEFAULT NULL COMMENT '瑕佹眰绮楃硻搴?,
  `w_roughness_actual` decimal(5, 3) NULL DEFAULT NULL COMMENT '瀹為檯绮楃硻搴?,
  `w_status` tinyint NULL DEFAULT 0 COMMENT '鐘舵€侊紙0-寰呭姞宸ワ紝1-鍔犲伐涓紝2-宸插畬鎴愶紝3-涓嶅悎鏍硷級',
  `w_task_id` bigint NULL DEFAULT NULL COMMENT '鍏宠仈浠诲姟ID',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '鍒涘缓鏃堕棿',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_workpiece_id`(`w_workpiece_id` ASC) USING BTREE,
  INDEX `idx_status`(`w_status` ASC) USING BTREE,
  INDEX `idx_task_id`(`w_task_id` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '宸ヤ欢淇℃伅琛? ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of workpiece_table
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
