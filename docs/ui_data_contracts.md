# UI <-> API 数据契约说明

本文档汇总 UI 与后端之间目前使用的主要 JSON 字段，便于 API、主控程序或自动化脚本生成/模拟数据时对齐格式。除非特别说明，所有路径均以 `http://<host>:<port>/api` 为前缀。

---

## 1. 状态数据（`/ws/status` + `/status/test_payload`）

WebSocket `/ws/status` 周期推送的载荷会被 `Datas.StatusDatas.ingest()` / `DriveInfoView.qml` / `StatusLightAlarmView.qml` 等组件消费。主控程序或测试窗口可通过 `POST /status/test_payload` 写入同样的字段。

### 1.1 顶层字段

| 字段 | 类型 | 说明 | UI 消费位置 |
| ---- | ---- | ---- | ------------ |
| `state` | string | 设备状态，常见值 `IDLE/RUNNING/PAUSED/FAULT` | 页头运行状态、DriveInfo 卡片 |
| `run_mode` / `runMode` | string | 当前运行模式 | DeviceInfo 卡片 |
| `serial_number` / `serialNumber` | string | 机台序列号 | DeviceInfo 卡片 |
| `tool_usage` / `toolUsage` | string/number | 刀具使用率 | DeviceInfo 卡片 |
| `tool_life` / `toolLifetime` | string | 刀具寿命 | DeviceInfo 卡片 |
| `particle_count` / `particleTotal` | number | 粒子总量 | CuttingStatistics |
| `plane_height` / `planeHeight` | number/string | 平面高度 | CuttingStatistics |
| `feed_rate` / `cutting_speed` | number | 切削速度（mm/s） | DriveInfo 卡片 |
| `travel_speed` / `motion_speed` | number | 移动速度 | DriveInfo 卡片 |
| `spindle_rpm` | number | 主轴转速 | DriveInfo + 折线图 |
| `spindle_torque` | number | 主轴扭矩 | DriveInfo + 折线图 |
| `seriesA` | number | 转速曲线备用值；若存在则用于 `Datas.StatusDatas.seriesA` | RpmChart |
| `seriesB` | number | 扭矩曲线备用值 | TorqueChart |
| `alerts` | array | 形式 `[{level, message}]` 的告警列表 | 测试窗口日志，自行扩展 |

### 1.2 位置与姿态

- `position`: 对象 `{ "x": float, "y": float, "z": float, "theta": float }`。DriveInfo 卡片逐项显示，缺失时以 `-` 填充。

### 1.3 指示灯状态

多个容器皆可提供灯光状态，`StatusLightAlarmView` 会按顺序查找：

- `statusLights`, `lightStates`, `lights`, `light_status`, `lightState`, `extras`，以及顶层对象本身。  
  每个容器中的 key 允许命名变体（例如 `camera_state`、`cameraStatus` 被视作 `camera`）。
- 标准键值：`camera`, `spindle`, `device`, `interlock`, `server`。取值可为 `RUNNING/READY/FAULT/WARNING` 等字符串或布尔值。

### 1.4 其他兼容字段

`DeviceInfoData.applySnapshot()` 会尝试兼容下列别名：

- `runMode` ↔ `run_mode`；`serialNumber` ↔ `serial_number`。
- `toolModel` / `tool_model` / `toolName`。
- `toolDiameter` / `cutter_diameter`。
- `toolLifetime` / `tool_life`。
- `toolUsage` / `tool_usage`。
- `planeHeight` / `plane_height`。
- `particleTotal` / `particle_count`。

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
  },
  "seriesA": 2350,
  "seriesB": 0.58
}
```

---

## 2. 切削数据（`GET /cutting` + `/cutting/test_payload`）

`Datas.CuttingDatas.update()` 消费 `/api/cutting` 的 JSON，并为 `CuttingStatisticsView.qml` 提供统计指标。

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `feed_rate` | number | 切削速度（mm/s） |
| `downfeed_target` | number | 目标进给量 |
| `downfeed_current` | number | 当前累计进给量 |
| `removal_current` | number | 已切削体积（mm³） |
| `removal_expected` | number | 预计总切削体积 |
| `torque` | number | 当前扭矩 |
| `torque_max` | number | 历史最大扭矩（后端会自动维持最大值） |
| `elapsed_sec` | number | 累计耗时（秒） |

> `Datas.CuttingDatas.removalRemaining = removal_expected - removal_current`；`CuttingStatisticsView` 也会跟踪 `maxFeedRate`，当新 `feed_rate` 更大时更新。

---

## 3. 配置&元数据

UI 仍依赖以下 REST 接口获取额外信息，生成的字段与 `DeviceInfoData` 兼容：

| 接口 | 说明 | 关键字段 |
| ---- | ---- | -------- |
| `GET /config/meta` | 硬件/工装元数据 | `board_serial`, `cutter_diameter`, `tool_life`, `particle_count`, `plane_height` |
| `GET /config/settings` | 刀具表等配置 | `tool_table[0].name / code` 用于推导 `toolModel` |

---

## 4. 主控程序命令行摘要

`python -m app.controller.main` 通过 REST 将上述字段注入后端，可选参数：

| 参数 | 默认值 | 说明 |
| ---- | ------ | ---- |
| `--base` | `http://127.0.0.1:8010/api` | API 基地址 |
| `--scenario` | `app/controller/sample_scenarios.json` | 场景文件，可多次指定 |
| `--merge` | `False` | 是否增量合并字段 |
| `--loop` | `False` | 循环播放 |
| `--interval` | `2.0` | 未开启 `--respect-delay` 时的默认间隔 |
| `--respect-delay` | `False` | 使用场景中定义的 `delay` |
| `--reset-on-exit` | `False` | 退出时自动调用 `DELETE` 清理覆盖 |

---

## 5. 开发提示

1. **字段兼容策略**：UI 组件会尝试多种命名别名，如需扩展新的字段，建议保持驼峰/下划线两种写法兼容。
2. **位置与姿态**：`position` 未提供某坐标时 UI 会显示 `-`。若姿态字段不需要，可省略。
3. **指示灯**：字符串不区分大小写，常用映射：`RUNNING/READY/FAULT/WARNING` → 正常/警告/报警，布尔值 `true/false` → 正常/报警。
4. **测试入口**：UI F12 测试窗口的“测试数据注入”面板就是上述接口的调用封装，观察按钮动作有助于确认格式。

