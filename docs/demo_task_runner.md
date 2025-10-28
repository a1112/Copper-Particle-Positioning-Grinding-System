# demo_task_runner.py 运行逻辑说明

本文档梳理 `app/controller/demo_task_runner.py` 的核心职责、数据库交互流程以及可扩展要点，便于后续将该模拟执行器替换为真实设备驱动程序或接入其他数据库接口实现。

## 1. 模块定位

`DemoTaskRunner` 是一个轻量级的调度器，用于在本地演示环境中模拟“采集 → 控制 → 执行”三段式流程。它通过定时调用 `tick()`：

1. 确保数据库存在必要的初始数据；
2. 轮询 `task_table` 中的待处理任务；
3. 更新任务状态并生成示例算法/图像产物；
4. 将执行结果反馈到 `status_table`、`record_table` 等表；
5. 根据需要向 `hardware_task_queue` 追加模拟的底层控制命令；
6. 保持 `status_table.status_time` 的心跳，供上层监控判断“执行层是否在线”。

该模块配合 `http_prod` 控制器及 API 层，可以在没有真实设备的情况下完成 UI 的全流程联调。

## 2. 数据库交互概览

`DemoTaskRunner` 通过 SQLAlchemy `session_factory` 操作以下模型（定义于 `app/db/models/MzPoliShineDB.py`）：

| 表名 | 用途 | 关键字段（片段） |
| --- | --- | --- |
| `status_table` | 设备总体状态与控制模式 | `c_control_mode`（0 本地/1 远程）、`c_run_status`（0 待机/1 就绪/2 运行等）、`status_time`（心跳时间） |
| `workpiece_table` | 当前演示用工件 | `w_workpiece_id`、`w_workpiece_type`、`w_material` 等。Demo 初始化时会插入一条默认记录。 |
| `task_table` | 任务队列（采集/执行/控制） | `t_task_type`（10=CAPTURE、20=EXECUTE、30=CONTROL）、`t_status`（0=排队、1=执行中、2=完成、3=失败）、`t_payload`、`t_status_detail`、`t_record_id` |
| `record_table` | 采集结果与算法数据 | `r_progress_data`（阶段标识）、`r_camera_data`（示例相机信息）、`r_algorithm_data`（路径/命令数据） |
| `hardware_task_queue`（可选） | 底层控制任务队列 | `task_type`、`task_params`。只有在创建 `DemoTaskRunner` 时传入 `task_writer` 才会写入。 |

对应的数据流如下：

1. **任务发现**：读取 `task_table` 中 `t_task_type` 为指定枚举、`t_status` 为 `PENDING`/`RUNNING` 的记录。
2. **状态流转**：进入 `RUNNING` 时写入 `t_status_detail.phase`、`started_at`、`updated_at`；完成后写入 `finished_at` 并标记 `COMPLETED`。
3. **采集阶段** (`CAPTURE`)：
   - 调用 `_materialise_capture_payload` 生成示例图像/算法文件，更新 `record_table` 记录；
   - 若尚不存在对应的控制任务，则自动写入一条 `CONTROL` 任务，`t_payload.commands` 为三条示例控制指令。
4. **控制阶段** (`CONTROL`)：
   - 当任务完成时，遍历 `commands` 列表，将命令转换为 `ControlInstruction` 并通过 `_task_writer`（若存在）写入 `hardware_task_queue`，模拟下发到执行层。
5. **执行阶段** (`EXECUTE`)：
   - 标注执行完成、刷新 `status_table` 和 `record_table.r_progress_data` 为 `execute_completed`。
6. **心跳刷新**：
   - `_heartbeat_status_table` 每次 `tick` 都更新 `status_table.status_time = datetime.utcnow()`，供控制器检测执行层离线超时。

## 3. 任务状态字段说明

### 3.1 `task_table` 相关字段

| 字段 | 说明 | Demo 写入方式 |
| --- | --- | --- |
| `t_task_type` | 任务类型枚举：10=CAPTURE、20=EXECUTE、30=CONTROL | 由上游（如 `http_prod`）写入。 |
| `t_status` | 0=排队、1=执行中、2=完成、3=失败 | Demo 将 `PENDING` → `RUNNING` → `COMPLETED`。 |
| `t_payload` | 附加参数（JSON） | CAPTURE：保存目标目录、备注等；CONTROL：保存 `commands` 列表；EXECUTE：保存 `record_id`。 |
| `t_status_detail` | 过程状态（JSON） | Demo 维护 `phase` / `started_at` / `updated_at` / `finished_at`，供前端显示执行详情。 |
| `t_record_id` | 关联的 `record_table` 记录 | CAPTURE/CONTROL/EXECUTE 全流程串联同一 `record_id`。 |

### 3.2 `record_table` 字段

| 字段 | 说明 | Demo 写入值 |
| --- | --- | --- |
| `r_progress_data` | 阶段信息 | `stage`= `capture_running` / `capture_completed` / `execute_running` 等，`updated_at` 为 `time.time()`。 |
| `r_camera_data` | 相机/采集信息 | Demo 写入演示帧数、曝光时间、图像目录等。 |
| `r_algorithm_data` | 算法结果 | 包含 `commands`（控制命令数组）、`path_preview`（可视化路径）、`artifact_folder` 等。 |

### 3.3 `status_table` 字段

| 字段 | 说明 | Demo 行为 |
| --- | --- | --- |
| `c_control_mode` | 控制模式（0=本地、1=远程） | 启动时强制置为 1，保证 UI 处于“远程可控”状态。 |
| `c_run_status` | 运行状态 | 进入各阶段时切换：1=READY、2=RUNNING、3=PAUSED 等。 |
| `c_machine_mode` | 机床模式 | 采集=2、控制=3、执行=4，完成后回到 1。 |
| `status_time` | 状态心跳 | 每次 `tick` 及状态变化时更新为 `datetime.utcnow()`。 |

## 4. `tick()` 内部执行顺序

```mermaid
flowchart TD
    start(开始 tick)
    ensureStatus[确保 status_table 处于远程/就绪]
    ensureWorkpiece[确保存在默认 workpiece]
    advanceCapture[推进 CAPTURE 任务]
    advanceControl[推进 CONTROL 任务]
    advanceExecute[推进 EXECUTE 任务]
    heartbeat[刷新 status_time]
    commit{有无变更?}
    end(结束)

    start --> ensureStatus --> ensureWorkpiece --> advanceCapture --> advanceControl --> advanceExecute --> heartbeat --> commit
    commit -->|是| end
    commit -->|否| end
```

每个 `_advance_xxx` 调用都会：

1. 通过 SQLAlchemy 查询待处理任务；
2. 在 `RUNNING` 阶段周期性更新 `t_status_detail.updated_at`；
3. 根据设定的 `_capture_duration`/_`_control_duration`/_`_execute_duration`（默认分别为 2.0/1.0/3.5 秒）模拟耗时；
4. 到达结束条件后调用 `_complete_xxx_task` 写入完成信息，并根据需要追加后续任务或产物。

## 5. 适配/替换指南

在对接真实设备或其他执行系统时，可按以下思路改造：

1. **保留数据契约**：`task_table`、`record_table`、`status_table` 字段与 API/UI 强绑定，建议继续沿用现有结构，或在替换前同步修改前端/后端契约。
2. **替换阶段逻辑**：将 `_advance_capture` / `_advance_control` / `_advance_execute` 中的模拟逻辑替换为真实的状态查询与回写；可引入异步任务或外部服务回调，但需保证最终更新 `t_status`、`t_status_detail`、`status_time`。
3. **处理 `commands`**：若算法输出格式不同，可在 `_complete_capture_task` 中调整 `r_algorithm_data` 与 `CONTROL` 任务 payload，确保 UI 能解析展示（对应字段在 `docs/ui_data_contracts.md` 有说明）。
4. **底层队列**：如果实际硬件对接不需要 `hardware_task_queue`，可以在初始化时将 `task_writer` 置为 `None`；若需要，可以实现自定义的写队列逻辑，并在 `_enqueue_control_command` 中调用。
5. **心跳机制**：UI 依赖 `status_table.status_time` 判断执行层是否超时（默认 10 秒）；真实实现应在合适时机更新该字段，或同步调整 `http_common.py` 中的 `self._runner_timeout`。
6. **产物存储**：`_materialise_capture_payload` 当前写入 `SaveData/record_xxxxxx` 目录，若有真实数据，可直接替换为实际路径或文件写入逻辑。

## 6. 相关配置与入口

- `app/controller/http_prod.py` 在启动时创建 `DemoTaskRunner` 并传入 `TaskQueueWriter`。
- `http_prod` 监听来自 HTTP 的控制指令，将命令写入 `task_table`，触发 `DemoTaskRunner` 的下一轮处理。
- 产物目录位置：`SaveData/record_<record_id>`；示例图像取自 `TestData/images`。

---

通过以上梳理，可以将 `DemoTaskRunner` 看作 “数据库 → 状态回写 → UI 联调” 的桥接层。在替换为真实执行程序时，重点保持数据结构与状态机同步更新，即可平滑迁移。***
