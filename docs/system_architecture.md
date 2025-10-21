# 系统架构说明

## 1. 总体结构

系统采用“三层”组织：

```
┌─────────────────────────────────────────────────────┐
│                  用户界面层 (UI/QML)                  │
│  - app/ui/qml/*: 界面视图、数据单例、异步工人            │
│  - app/ui/src/*: Python 桥接、图像处理                 │
│  - app/ui/cmake: C++ 编译版本，提升安全与运行速度         │
└──────────────▲───────────────────────────┬──────────┘
               │ WebSocket/HTTP JSON       │
┌──────────────┴───────────────────────────▼──────────┐
│               后端服务层 (FastAPI)                    │
│  - app/server/api: REST + WebSocket                 │
│  - app/server/business: 业务服务（Sim/Runtime）       │
│  - app/domain/status: 状态提供者/仓储/服务             │
└──────────────▲───────────────────────────┬──────────┘
               │ 驱动接口调用   / 数据库      │
┌──────────────┴───────────────────────────▼──────────┐
│               核心运行层 (Core/Devices)               │
│  - app/core: 状态机、配方、事件总线                     │
│  - app/process: 工艺编排与任务流                       │
│  - app/devices: 真实与模拟驱动实现                     │
└─────────────────────────────────────────────────────┘
```

UI 经 `app/ui/qml/works` 建立到后端的 WebSocket 连接，实时同步状态与日志；控制指令通过 REST 发送到业务服务，由业务层协调核心运行层执行。


## 2. 模块职责

### 2.1 核心运行层
- `app/core/state_machine.py`：加工状态机及事件转移。
- `app/process/orchestrator.py`：调度加工步骤、与设备交互。
- `app/devices/*`：封装主轴、运动、相机等设备接口，区分真实/模拟实现。

### 2.2 后端服务层
- `app/server/api`：FastAPI 应用入口、REST 控制、WebSocket 状态推送。
- `app/server/business`：业务服务抽象，`SimBusinessService` 与 `RuntimeBusinessService` 对应模拟/真实环境。
- `app/domain/status`：状态数据服务，整合不同 `StatusProvider`（模拟、生产）并向业务层提供统一接口。

### 2.3 UI 层
- `app/ui/qml/views`：界面组件（如 DriveInfo、Charts、Manage）。
- `app/ui/qml/datas`：单例数据模型（`StatusDatas`, `CuttingDatas`）。
- `app/ui/qml/works`：WebSocket 工作者，负责连接后端并更新数据模型。
- `app/ui/src/qml_bridge.py`：Python 向 QML 暴露的桥接对象。  
- `app/ui/qml.qrc` + `scripts/build_rcc.ps1`：QML 资源编译。


## 3. 数据流与关键交互

1. **状态推送**：后端 `ws_status` 周期性调用业务服务的 `fetch_status()`，取得 `StatusModel`，推送给前端。`StatusDatas.ingest()` 更新最新消息，并驱动各视图刷新，如 `DriveInfoView`、`StatusLightAlarmView`、`ElevationAreaChart`。
2. **日志推送**：`ws_logs` 从业务层读取日志队列，推送到 `LogDatas`。
3. **控制指令**：UI 调用 `Api.ApiClient` 的 POST 方法，业务服务接收 `ControlCommand` 并委托核心运行层执行（如急停、回零）。
4. **加工数据**：`CuttingWork` 轮询 `/cutting` HTTP 接口，更新 `CuttingDatas`，为 `CuttingStatisticsView` 等提供数据。
5. **模拟与真实切换**：`app/server/data/context.py` 默认注入 `SimBusinessService`，可在部署时切换为 `RuntimeBusinessService`，其内部使用真实设备和 `ProductionStatusProvider`。

### 新增：主控逻辑程序

独立的主控程序位于 `app/controller/main.py`，核心职责：

- 读取 JSON 场景文件（默认 `app/controller/sample_scenarios.json`），生成状态、位置、转速、切削量等完整载荷；
- 通过 HTTP（使用 `/status/test_payload` 与 `/cutting/test_payload`）向 Server 推送数据，Server 再驱动 UI；
- 支持循环播放、按场景延时、退出时自动清理覆盖数据等运行模式，可用于联调或模拟产线工况。*** End Patch*** End Patch
## 4. 运行时序 (示意)

```
UI.InfoManageView      Works.StatusWork     ws_status         BusinessService      StatusProvider
      |                       |                 |                      |                    |
      |<--QML load------------|                 |                      |                    |
      |                       |----connect----->|                      |                    |
      |                       |                 |----fetch_status----->|                    |
      |                       |                 |                      |----get_status----->|
      |                       |                 |<---StatusModel-------|<---status dict-----|
      |<--Datas.StatusDatas---|                 |                      |                    |
      |   repaint charts      |                 |                      |                    |
```


## 5. 部署要点

- **后端**：`python -m app.server.run_api` 启动 FastAPI；可通过环境变量或配置指定使用的业务服务/状态提供者。
- **前端**：`python -m app.main` 启动 PySide6/QML 应用；确保已执行 `pip install -r requirements.txt`。
- **静态资源**：修改 QML 后需运行 `powershell -File scripts/build_rcc.ps1` 以重生成 `qml.rcc`（若使用预编译资源）。
- **测试**：`python -m pytest`；对 API 可额外运行 `python scripts/smoke_api.py`。


## 6. 后续改进建议

1. **契约统一**：现前端对状态灯、剖面数据存在多字段兼容逻辑，建议在 `StatusModel` 中新增显式字段并文档化，降低耦合。
2. **WebSocket 节流**：对大数据（如剖面点集）可采用缓存+按需推送，避免每帧重复发送；前端 `StatusDatas` 也可加入差分更新策略。
3. **配置化注入**：通过配置文件或环境变量决定启用的 `BusinessService`、`StatusProvider`，并在 `app/server/run_api.py` 中自动加载。
4. **多语言支持**：利用 `qsTr()` 与 `.ts` 翻译文件，统一字符串编码，消除历史乱码问题。
5. **文档化流程**：补充设备接入说明、接口契约文档及序列图，方便新成员快速理解整体协作方式。

本说明将随代码迭代更新，建议在引入新模块或重构时同步维护。
