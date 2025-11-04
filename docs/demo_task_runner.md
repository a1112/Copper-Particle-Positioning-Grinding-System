# demo_task_runner.py 运行逻辑说明

本文档梳理 `app/controller/demo_task_runner.py` 的职责、数据库交互流程，以及在替换/扩展时需要关注的要点，帮助快速理解演示执行器的工作方式。

## 1. 模块定位

`DemoTaskRunner` 是一个轻量级调度器，用于在本地演示环境中模拟“采集 → 控制 → 执行”的完整流程。它会按固定周期调用 `tick()` 并完成以下动作：

1. 确保数据库存在必要的初始数据（默认工件、状态表等）；
2. 扫描 `hardware_task_queue` 中的待处理任务；
3. 推动任务状态机并生成示例算法/图像产物；
4. 将结果写回 `status_table`、`record_table` 等表；
5. 需要时向 `hardware_task_queue` 追加模拟的底层控制指令；
6. 刷新 `status_table.status_time` 作为心跳，供上层检测执行层在线状态。

> **启动方式**  
> 自 2025/10/28 起，`http_prod` 默认不再内嵌启动 Demo 任务执行器。需要演示时请手动运行：
> ```bash
> python -m app.controller.demo_task_runner
> ```
> 如确有需要，可在命令行增加 `--spawn-demo-runner` 与 HTTP 控制桥同启。

## 2. 数据库交互一览

`DemoTaskRunner` 通过 SQLAlchemy `session_factory` 操作以下模型（定义于 `app/db/models/MzPoliShineDB.py`）：

| 表名 | 用途 | 关键字段 |
| --- | --- | --- |
| `status_table` | 设备总体状态与控制模式 | `c_control_mode`（0=本地，1=远程）、`c_run_status`（0=待机，1=就绪，2=运行）、`status_time`（心跳） |
| `workpiece_table` | 当前演示工件 | `w_workpiece_id`、`w_workpiece_type`、`w_material` 等，启动时自动插入默认记录 |
| `record_table` | 采集结果与算法数据 | `r_progress_data`、`r_camera_data`、`r_algorithm_data` 等字段保存阶段产物 |
| `hardware_task_queue` | 任务队列（采集/执行/控制） | `task_type`（10=CAPTURE，20=EXECUTE，30=CONTROL）、`status`（0=排队，1=执行中，2=完成，3=失败）、`task_params`、`status_params` |

## 3. 任务推进要点

### 3.1 任务发现
- CAPTURE/CONTROL/EXECUTE 任务均存放在 `hardware_task_queue` 中；
- `task_type` 决定所属阶段；
- `status` 为 `PENDING` 或 `RUNNING` 的记录会被选中；
- `status_params.phase`、`started_at`、`updated_at`、`finished_at` 用于记录阶段细节，便于 UI 展示。

### 3.2 阶段内逻辑
1. **采集（CAPTURE）**
   - 任务转入运行态时更新 `status_params` 并标记 `record_table` 当前阶段；
   - 调用 `_materialise_capture_payload` 生成示例算法 JSON、复制演示图像；
   - 填充 `record_table.r_algorithm_data`、`r_camera_data`、`r_warning_data`；
   - 若无对应控制任务，则追加一条 `CONTROL` 任务（内含示例 commands）。
2. **控制（CONTROL）**
   - 完成后遍历示例 commands，转换为 `ControlInstruction` 并借助 `_task_writer.enqueue()` 写入硬件队列，模拟下发；
   - 同时更新 `status_table` 以反映设备状态。
3. **执行（EXECUTE）**
   - 结束时将 `record_table.r_progress_data` 标记为 `execute_completed`；
   - 更新 `status_table` 的运行状态与模式。

### 3.3 心跳
`_heartbeat_status_table()` 在每次 `tick` 时刷新 `status_table.status_time = datetime.utcnow()`，以便 `http_prod` 判断执行层是否超时。

## 4. 产物目录

- 算法/图像默认写入 `SaveData/record/<record_id>`；
- 示例图像复制自 `TestData/images`；
- 结构示例：
  ```
  SaveData/
    record/1/
      algorithm.json         # 包含 commands、path_preview
      image/
        color.png
        gray.png
        depth.png
        normal.png
  ```

## 5. 替换为真实执行程序时的建议

1. **保持数据契约**：`hardware_task_queue`、`record_table`、`status_table` 与 API/UI 紧密关联，字段调整需同步前后端；
2. **阶段逻辑替换**：可将 `_advance_*` 内的模拟逻辑换成真实设备状态查询与回写，确保状态更新语义一致；
3. **命令格式处理**：若算法输出与示例不同，可在 `_complete_capture_task` 中转换后写入 `task_params` 与 `r_algorithm_data`；
4. **底层任务队列**：如真实环境无需硬件队列，可不向 `DemoTaskRunner` 传入 `task_writer`，或替换 `_enqueue_control_command` 的实现；
5. **心跳策略**：`http_prod` 默认 10 秒超时，若心跳由其他系统维护，可调整 `TaskQueueWriter`/`DbStatusSource` 相关逻辑；
6. **异常与重试**：演示模式为最小实现，接入真实设备需补充异常处理、失败重试、详细日志等能力。

## 6. 相关入口

- 启动 demo 执行器：`python -m app.controller.demo_task_runner`
- 启动 HTTP 控制桥：`python -m app.controller.http_prod`  
  可选参数 `--spawn-demo-runner` 用于同进程启动 Demo 执行器
- API/UI 数据契约：参考 `docs/ui_data_contracts.md`

---

整体来看，`DemoTaskRunner` 可视作连接数据库、状态回放与 UI 联调的中间层。只要遵循 `hardware_task_queue` 与相关表的字段语义，就能在接入真实设备时平滑迁移。
