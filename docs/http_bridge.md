# HTTP 网桥工作流程

`HttpBusinessService` 构成 API 进程与外部主控之间的 HTTP 桥接层，主要职责如下：
- FastAPI 会注入 `/bridge/status`、`/bridge/cutting`、`/bridge/logs`、`/bridge/controller`、`/bridge/ping` 路由。控制器向这些端点 `POST` 数据即可，服务端会写入线程安全的 `HttpDataStore`。
- 控制指令由 API 透过 `HttpControlClient` 发送到主控暴露的 `/control` 端点，主控返回的结果会原样反馈给前端。
- 启动 API 时设置 `COPPER_DATA_MODE=http`（或配置 `data_mode="http"`）即可启用 HTTP 网桥模式；默认桥接地址为 `http://<APP_HOST>:<APP_PORT>/bridge`。
- 控制器侧可选择：
  1. `python -m app.controller.main --transport http`：读取场景文件循环推送；
  2. `python -m app.controller.http_sim`：默认连接测试库 `mysql+pymysql://mz:123456@192.168.2.32/MzPoliShineDB?charset=utf8mb4` 获取 `status_table`，也可通过 `--disable-db` 完全使用内置模拟数据；
  3. `python -m app.controller.http_prod`：绑定生产库 `mysql+pymysql://remote_user:123456@192.168.1.214/MzPoliShineDB?charset=utf8mb4`，实时读取 `status_table`。
- 以上控制脚本会把 `run.start`/`run.stop` 等控制指令同步写入 `hardware_task_queue`（字段包含 task_id、task_type、task_params 等），便于后端/硬件调度记录命令流水。
- 所有日志最终都会写入 `app.server.utils.logs` 的环形缓冲；WebSocket `/ws/logs` 会从该缓冲推送历史与增量，保证 UI 能实时看到 HTTP 模式下的日志。

> 小提示：通过环境变量 `COPPER_HTTP_BRIDGE_BASE`、`COPPER_HTTP_CONTROL`、`COPPER_HTTP_TIMEOUT` 可以自定义桥接地址、控制端点和超时时间。
