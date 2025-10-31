# 系统架构说明

## 1. 分层结构

系统按“前端展示 → API 网关 → 核心流程”的方式组织：

```
┌─────────────────────────────────────────────────────────┐
│                     用户界面（PySide6/QML）             │
│  - app/ui/qml/*: 视图、图表、数据模型、异步工作器        │
│  - app/ui/src/*: Python ↔ QML 桥接、模型封装             │
│  - app/ui/cmake: 可选的 C++ 扩展（性能焦点）             │
└─────────────────────────────────────────────────────────┘
                 │ WebSocket / HTTP JSON
┌─────────────────────────────────────────────────────────┐
│                     服务层（FastAPI）                   │
│  - app/server/api: REST + WebSocket                     │
│  - app/server/business: 业务服务（Sim / Runtime）        │
│  - app/domain/status: 状态提供器 / 聚合 / 转换            │
└─────────────────────────────────────────────────────────┘
                 │ 设备接口 / 数据库
┌─────────────────────────────────────────────────────────┐
│                  核心流程与设备层                       │
│  - app/core: 状态机、事件系统                           │
│  - app/process: 研磨流程编排                            │
│  - app/devices: 真实/模拟驱动实现                       │
└─────────────────────────────────────────────────────────┘
```

UI 中 `app/ui/qml/works` 目录的 Work 对象负责建立 WebSocket 连接，实时同步状态、日志与控制命令；REST 指令由 `Api.ApiClient` 发送到业务层，业务层再调用设备层执行。

## 2. 模块职责

### 2.1 核心流程与设备层
- `app/core/state_machine.py`：统一配置状态转换与事件。
- `app/process/orchestrator.py`：调度研磨步骤、刀具补偿、设备联动。
- `app/devices/*`：封装 IO、运动控制、相机等设备接口，包含真实与模拟实现。

### 2.2 服务层
- `app/server/api`：FastAPI 应用，暴露 REST / WebSocket。
- `app/server/business`：`SimBusinessService`、`RuntimeBusinessService` 等负责协调数据流。
- `app/domain/status`：状态聚合器，整合不同 `StatusProvider`（模拟、生产、录播等），向 UI 输出统一结构。

### 2.3 UI 层
- `app/ui/qml/views`：界面组件（DriveInfo、Charts、Manage 等）。
- `app/ui/qml/datas`：数据模型（`StatusDatas`、`CuttingDatas` 等），负责解析 API 响应。
- `app/ui/qml/works`：异步任务，维护 WebSocket 连接、防抖与重连策略。
- `app/ui/src/qml_bridge.py`：Python 与 QML 的桥接对象。
- `app/ui/qml.qrc` + `scripts/build_rcc.ps1`：QML 资源打包脚本。

## 3. 关键数据流

1. **状态推送**：`ws_status` → `BusinessService.fetch_status()` → `StatusModel` → `StatusDatas.ingest()` → `DriveInfoView` / `StatusLightAlarmView` / 图表刷新。
2. **日志推送**：`ws_logs` → `LogDatas`，供 UI 测试面板查看历史与增量。
3. **控制命令**：UI 调用 `Api.ApiClient` 的 `POST /control/*`，业务层生成 `ControlCommand` 并路由至设备层执行（急停、复位、停止等）。
4. **数据源切换**：`app/server/data/context.py` 根据配置注入 `SimBusinessService`、`RpcBusinessService` 或 `RuntimeBusinessService`，并切换 `StatusProvider`。

### 主控器逻辑简述

`app/controller/main.py` 负责：
- 读取 JSON 场景（默认 `app/controller/sample_scenarios.json`），生成状态、轨迹、日志等事件序列。
- 通过 gRPC/HTTP 把状态与日志推送至服务器，服务器再通过 WebSocket 同步给 UI。
- 支持循环播放、尊重场景内延迟、自动退出或持续运行模式。

## 4. 典型时序（简化）

```
UI.InfoManageView      Works.StatusWork     ws_status     BusinessService     StatusProvider
      |                       |                 |                 |                 |
      |<--load QML-----------|                 |                 |                 |
      |                       |----connect----->|                 |                 |
      |                       |                 |----fetch------->|                 |
      |                       |                 |                 |----get--------->|
      |                       |                 |<---StatusModel--|<---status dict--|
      |<--StatusDatas.ingest--|                 |                 |                 |
      |   repaint charts      |                 |                 |                 |
```

## 5. 构建与运行

- **后端**：`python -m app.server.run_api`，通过环境变量或 CLI 选择业务服务 / 状态提供者。
- **前端**：`python -m app.main`，确保已执行 `pip install -r requirements.txt`。
- **资源**：修改 QML 后运行 `powershell -File scripts/build_rcc.ps1` 生成 `qml.rcc`。
- **测试**：`python -m pytest` 或 `python scripts/smoke_api.py`。

## 6. 后续改进建议

1. **字段统一**：持续收敛 `StatusModel` 字段，避免前端解析多套命名。
2. **WebSocket 压测**：评估推送频率与 UI 回执，必要时引入批量合并。
3. **可插拔数据源**：通过配置文件/命令行显式选择 `BusinessService` 与 `StatusProvider`，方便切换真实设备。
4. **多语言支持**：继续通过 `qsTr()` + `.ts` 文件维护文案，消除历史乱码。
5. **文档同步**：把硬件接口、通信协议等技术文件集中在 `docs/export/`，保持与代码版本一致。
