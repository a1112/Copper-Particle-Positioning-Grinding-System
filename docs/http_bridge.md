# HTTP 网桥工作流程

`HttpBusinessService` 负责在 API 进程与外部主控之间建立 HTTP 桥接层，整体职责如下：

1. FastAPI 注入 `/bridge/status`、`/bridge/cutting`、`/bridge/logs`、`/bridge/controller`、`/bridge/ping` 路由。控制器对这些端点执行 `POST` 即可，服务端会写入线程安全的 `HttpDataStore`。
2. 控制指令由 API 通过 `HttpControlClient` 转发到主控暴露的 `/control` 端点，主控返回结果后原样反馈给前端。
3. 启动 API 时设置 `COPPER_DATA_MODE=http`（或 `config.data_mode="http"`）即可启用 HTTP 网桥；默认桥接地址为 `http://<APP_HOST>:<APP_PORT>/bridge`。
4. 控制器侧可选择：
   - `python -m app.controller.main --transport http`：读取场景文件循环推送。
   - `python -m app.controller.http_sim`：连接测试库 `mysql+pymysql://mz:123456@192.168.2.32/MzPoliShineDB?charset=utf8mb4` 获取 `status_table`，或通过 `--disable-db` 使用内置模拟数据。
   - `python -m app.controller.http_prod`：绑定生产库 `mysql+pymysql://remote_user:123456@192.168.1.214/MzPoliShineDB?charset=utf8mb4`，实时读取 `status_table`。
5. 上述控制脚本会把 `run.start`/`run.stop` 等指令同步写入 `hardware_task_queue`（包含 `task_id/task_type/task_params` 等字段），便于硬件调度与审计。
6. 所有日志写入 `app.server.utils.logs` 的环形缓冲；WebSocket `/ws/logs` 会从该缓冲推送历史与增量，确保 UI 在 HTTP 模式下也能实时查看日志。

> 可通过环境变量 `COPPER_HTTP_BRIDGE_BASE`、`COPPER_HTTP_CONTROL`、`COPPER_HTTP_TIMEOUT` 自定义桥接地址、控制端点与超时时间。
