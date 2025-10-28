# demo_task_runner.py 运行逻辑说明

本文档概述 `app/controller/demo_task_runner.py` 的职责、数据库交互流程以及替换/扩展时的注意事项，帮助快速理解执行器 Demo 的工作方式。

## 1. 模块定位

`DemoTaskRunner` 是一个轻量级调度器，用于在本地演示环境中模拟“采集 → 控制 → 执行”的完整流程。它会按照固定周期调用 `tick()`，完成以下任务：

1. 确保数据库存在必要的初始数据（默认工件、Status 表等）；
2. 扫描 `task_table` 中的待处理任务；
3. 更新任务状态并生成示例算法/图像产物；
4. 将执行结果写回 `status_table`、`record_table` 等表；
5. 视情况向 `hardware_task_queue` 追加模拟的底层控制命令；
6. 维持设备心跳（更新 `status_table.status_time`）供上层检测执行层是否在线。

> **启动方式：** 自 2025/10/28 起，`http_prod` 默认不再内嵌启动 Demo 任务执行器。需要演示时，请手动运行：
>
> ```bash
> python -m app.controller.demo_task_runner
> ```
>
> 若确实需要随 `http_prod` 一起启动，可在命令行添加 `--spawn-demo-runner`。

## 2. 数据库交互一览

`DemoTaskRunner` 通过 SQLAlchemy `session_factory` 操作以下模型（定义于 `app/db/models/MzPoliShineDB.py`）：

| 表名 | 用途 | 关键字段 |
| --- | --- | --- |
| `status_table` | 设备总体状态与控制模式 | `c_control_mode`（0=本地，1=远程）、`c_run_status`（0=待机，1=就绪，2=运行，3=暂停，4=停止）、`status_time`（心跳） |
| `workpiece_table` | 当前演示工件 | `w_workpiece_id`、`w_workpiece_type`、`w_material` 等，Demo 启动时会自动插入默认记录 |
| `task_table` | 任务队列（采集/执行/控制） | `t_task_type`（10=CAPTURE，20=EXECUTE，30=CONTROL）、`t_status`（0=排队，1=执行中，2=完成，3=失败）、`t_payload`、`t_status_detail` |
| `record_table` | 采集结果与算法数据 | `r_progress_data`（阶段标识）、`r_camera_data`（示例相机信息）、`r_algorithm_data`（路径/命令数据） |
| `hardware_task_queue`（可选） | 底层控制任务队列 | `task_type`、`task_params`。只有在创建 `DemoTaskRunner` 时传入 `task_writer` 才会写入。 |

### 2.1 任务推进要点

1. **任务发现：** 查询 `task_table` 中 `t_task_type` 为目标类型、`t_status` 为 `PENDING`/`RUNNING` 的记录。
2. **状态流转：** 进入 `RUNNING` 时写入 `t_status_detail.phase`、`started_at`、`updated_at`，完成后记录 `finished_at` 并改为 `COMPLETED`。
3. **采集阶段（CAPTURE）：**
   - 调用 `_materialise_capture_payload` 生成示例图像、算法 JSON，并更新 `record_table`；
   - 若尚无对应的控制任务，则自动新增一条 `CONTROL` 任务，`t_payload.commands` 包含三条示例控制指令。
4. **控制阶段（CONTROL）：**
   - 任务完成时遍历 `commands`，转换为 `ControlInstruction`，通过 `_task_writer.enqueue(...)` 写入 `hardware_task_queue`（如果提供）以模拟下发。
5. **执行阶段（EXECUTE）：**
   - 标记任务完成，更新 `status_table` 与 `record_table.r_progress_data` 中的阶段信息。
6. **心跳更新：**
   - `_heartbeat_status_table()` 每次 `tick` 都会刷新 `status_table.status_time = datetime.utcnow()`，供 `http_prod` 判断执行层超时。

### 2.2 关键字段说明

- `cutting_status_table`（新增，单条记录）用于向 HTTP 控制器提供切削实时数据，字段如下：
  - `feed_rate`：进给速度（mm/s）
  - `torque`：主轴扭矩（N·m）
  - `elapsed_sec`：累计执行时长（秒）
  - `spindle_rpm`：主轴转速（rpm）
  - `updated_time` / `created_time`

  该表主键恒定为 1，运行前请手动插入初始数据，并在需要时更新这些数值。
  示例建表 / 初始化 SQL：

  ```sql
  CREATE TABLE IF NOT EXISTS cutting_status_table (
      id BIGINT PRIMARY KEY CHECK (id = 1),
      feed_rate DECIMAL(10,3) NOT NULL DEFAULT 0,
      torque DECIMAL(10,3) NOT NULL DEFAULT 0,
      elapsed_sec DECIMAL(10,3) NOT NULL DEFAULT 0,
      spindle_rpm DECIMAL(10,2) NOT NULL DEFAULT 0,
      created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  );

  INSERT INTO cutting_status_table (id, feed_rate, torque, elapsed_sec, spindle_rpm)
  VALUES (1, 0, 0, 0, 0)
  ON DUPLICATE KEY UPDATE updated_time = NOW();
  ```

- `task_table.t_payload`：CAPTURE 保存目标目录与备注；CONTROL 保存 `commands`；EXECUTE 保存关联 `record_id`。
- `task_table.t_status_detail`：记录 `phase`、`started_at`、`updated_at`、`finished_at` 等细节，供 UI 展示。
- `record_table.r_algorithm_data`：包含 `commands`（控制命令列表）、`path_preview`（路径可视化数据）、`artifact_folder`（文件夹路径）等。
- `status_table.c_control_mode`：强制设为 1（远程），保证 UI 可执行控制按钮。

## 3. tick() 内部流程

```mermaid
flowchart TD
    start(开始 tick)
    ensureStatus[确保 status_table 处于远程/就绪]
    ensureWorkpiece[确保存在默认工件]
    advanceCapture[推进 CAPTURE 任务]
    advanceControl[推进 CONTROL 任务]
    advanceExecute[推进 EXECUTE 任务]
    heartbeat[刷新 status_time]
    commit{是否有变更?}
    end(结束)

    start --> ensureStatus --> ensureWorkpiece --> advanceCapture --> advanceControl --> advanceExecute --> heartbeat --> commit
    commit -->|是| end
    commit -->|否| end
```

各 `_advance_xxx` 会：

1. 查询待处理任务；
2. 进入执行态时更新 `t_status_detail`；
3. 根据 `_capture_duration` / `_control_duration` / `_execute_duration`（默认 2.0 / 1.0 / 3.5 秒）模拟耗时；
4. 条件满足后调用 `_complete_xxx_task` 写入结果并追加后续任务/产物。

## 4. 产物目录

- 算法/图像文件默认写入 `SaveData/record_<record_id>`；
- 示例图像复制自 `TestData/images`；
- 结构示例：  
  ```
  SaveData/
    record_000001/
      algorithm.json         # 包含 commands、path_preview
      image/
        color.png
        gray.png
        depth.png
        normal.png
  ```

## 5. 替换为真实执行程序时的建议

1. **保持数据契约：** `task_table`、`record_table`、`status_table` 与 API/UI 强绑定，若调整字段需同步更新前后端。
2. **替换阶段逻辑：** 将 `_advance_*` 中的模拟逻辑替换为真实设备状态查询与回写；可结合线程/异步或消息队列，但需确保最终写入任务状态与心跳。
3. **处理命令格式：** 若算法输出与示例不同，可在 `_complete_capture_task` 中调整 `t_payload`/`r_algorithm_data`，或在对接算法模块时统一格式。
4. **底层任务队列：** 如果实际场景不需要 `hardware_task_queue`，可不传入 `task_writer`；如需，可在 `_enqueue_control_command` 内扩展为真正的硬件接口。
5. **心跳策略：** `http_prod` 当前以 10 秒为超时阈值，若心跳由其他系统维护，可修改 `http_common.py` 中的 `self._runner_timeout` 或改写 `task_runner_health` 逻辑。
6. **错误处理：** Demo 以最小化示例为主，真实场景应补充异常捕获、失败重试、日志等功能。

## 6. 相关入口

- 启动 demo 执行器：`python -m app.controller.demo_task_runner`
- 启动 HTTP 控制桥：`python -m app.controller.http_prod`  
  - 如需同时启动 Demo 执行器，加 `--spawn-demo-runner`（默认关闭）。
- API/前端相关数据契约：见 `docs/ui_data_contracts.md`

---

通过以上说明，可以将 `DemoTaskRunner` 视作“数据库 ↔ 状态回写 ↔ UI 联调”的中间层。在接入真实设备时，重点在于保持状态/任务字段更新一致，即可平滑替换。***
