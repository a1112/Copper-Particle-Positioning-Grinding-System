# UI <-> API 数据契约说明

本文档汇总 UI 与后端之间使用的主要 JSON 字段，方便 API、主控程序或自动化脚本在生成模拟数据时保持一致。除特别说明，所有路径均以 `http://<host>:<port>/api` 为前缀。

---

## 1. 状态数据（`/ws/status` + `/status/test_payload`）

WebSocket `/ws/status` 周期推送的载荷会被 `Datas.StatusDatas.ingest()`、`DriveInfoView.qml`、`StatusLightAlarmView.qml` 等组件消费。`POST /status/test_payload` 可写入相同字段用于调试。

### 1.1 顶层字段

| 字段 | 类型 | 说明 | UI 消费位置 |
| ---- | ---- | ---- | ------------ |
| `state` | string | 设备状态，常见 `IDLE/RUNNING/PAUSED/FAULT` | 页头状态标签、DriveInfo 卡片 |
| `run_mode` / `runMode` | string | 当前运行模式 | DeviceInfo 卡片 |
| `serial_number` / `serialNumber` | string | 机台序列号 | DeviceInfo 卡片 |
| `particle_count` / `particleTotal` | number | 粒子总量 | CuttingStatistics |
| `plane_height` / `planeHeight` | number/string | 平面高度 | CuttingStatistics |
| `feed_rate` / `cutting_speed` | number | 切削速度（mm/s） | DriveInfo 卡片 |
| `travel_speed` / `motion_speed` | number | 移动速度 | DriveInfo 卡片 |
| `spindle_rpm` | number | 主轴转速 | DriveInfo + RpmChart |
| `spindle_torque` | number | 主轴扭矩 | DriveInfo + TorqueChart |
| `seriesA` | number | 转速曲线备用值 | RpmChart |
| `seriesB` | number | 扭矩曲线备用值 | TorqueChart |
| `alerts` | array | `[{level, message}]` 告警列表 | 测试窗口日志 |

### 1.2 位置与姿态

- `position`: `{ "x": float, "y": float, "z": float, "theta": float }`。DriveInfo 卡片逐项显示，缺失时以 `-` 填充。

### 1.3 指示灯状态

多个容器都可以提供灯光状态，`StatusLightAlarmView` 会按顺序查找以下键：`statusLights`, `lightStates`, `lights`, `light_status`, `lightState`, `extras` 以及顶层对象本身。 

- 标准键值：`camera`, `spindle`, `device`, `interlock`, `server`。
- 取值可为 `RUNNING/READY/FAULT/WARNING` 等字符串，也可为布尔值。命名允许变体（例如 `camera_state`、`cameraStatus` 会被归一到 `camera`）。

### 1.4 信息映射（DeviceInfoData / ToolInfoData）

`DeviceInfoData.applySnapshot()` 会尝试匹配以下字段：
- `runMode / run_mode`
- `serialNumber / serial_number`
- `planeHeight / plane_height`
- `particleTotal / particle_count`

`ToolInfoData.applySnapshot()` 会匹配：
- `toolModel / tool_model / toolName`
- `toolDiameter / tool_diameter / cutter_diameter`
- `toolLifetime / tool_life`
- `toolUsage / tool_usage`

### 1.5 示例载荷

```json
{
  "state": "RUNNING",
  "run_mode": "AUTO",
  "serial_number": "SIM-0002",
  "position": { "x": 125.4, "y": 42.8, "z": -0.46, "theta": 0.75 },
  "spindle_rpm": 2350,
  "spindle_torque": 0.58,
  "feed_rate": 24.0,
  "travel_speed": 52.0,
  "statusLights": {
    "camera": "READY",
    "spindle": "RUNNING",
    "device": "RUNNING",
    "interlock": true,
    "server": true
  }
}
```

---

## 2. 切削数据（`/cutting` + `/cutting/test_payload`）

`CuttingWork` 每 1s 轮询 `/cutting`，写入 `CuttingDatas` 并驱动统计面板。

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `feed_rate` | number | 进给速度（mm/s）|
| `downfeed_target` | number | 目标下刀量（mm）|
| `downfeed_current` | number | 当前下刀量（mm）|
| `removal_current` | number | 当前去除量（mm³ 或 μm）|
| `removal_expected` | number | 计划去除量 |
| `torque` | number | 当前扭矩 |
| `torque_max` | number | 历史最大扭矩（用于峰值提醒）|
| `elapsed_sec` | number | 已加工时长 |

当字段缺失时，UI 会保留上一帧或以 `0`/`-` 填充。

---

## 3. 配置 / 元数据（`/config/meta`）

配置接口为静态信息，主要绑定以下视图：

| 字段 | 说明 | 消费位置 |
| ---- | ---- | ---- |
| `board_serial` | 控制板序列号 | DeviceInfo |
| `machine_model` | 机床型号 | DeviceInfo |
| `cutter_diameter` | 刀具直径 | ToolInfo |
| `tool_life` | 额定寿命 | ToolInfo |
| `coolant` | 冷却方式 | StatusOverview |
| `nodes` | 引用 `MzPoliShine.km` 导图的层级描述 | InfoManage/Meta 对话框 |

该接口也会透出 `tool_table`、`table_limits` 等配置，供流程控制或算法模块加载。

---

## 4. 编写模拟数据的要点

1. 字段名支持驼峰与下划线，建议两种命名同时输出，便于前端兼容。
2. 时间戳统一使用秒级浮点或 ISO8601 字符串；UI 侧会优先解析浮点值。
3. 在测试脚本中调用 `POST /status/test_payload?merge=true` / `POST /cutting/test_payload?merge=true` 可在不影响其余字段的情况下局部更新。
4. WebSocket 在断线时会自动回放最新一次的快照，务必保证 JSON 可被重复解析。
5. 添加新字段时同步更新：`docs/ui_data_contracts.md`、`StatusDatas.qml`、`CuttingDatas.qml` 以及相关单元测试。
