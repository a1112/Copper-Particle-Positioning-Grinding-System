# HTTP 网桥工作流程

`HttpBusinessService` 构成 API 进程与外部主控之间的 HTTP 桥接层，主要职责如下：
- FastAPI 会注入 `/bridge/status`、`/bridge/cutting`、`/bridge/logs`、`/bridge/controller`、`/bridge/ping` 路由。控制器向这些端点 `POST` 数据即可，服务端会写入线程安全的 `HttpDataStore`；
- 控制指令由 API 透过 `HttpControlClient` 发送到主控暴露的 `/control` 端点，主控返回的结果会原样反馈给前端；
- 启动 API 时设置 `COPPER_DATA_MODE=http`（或配置 `data_mode="http"`）即可启用 HTTP 网桥模式；默认桥接地址为 `http://<APP_HOST>:<APP_PORT>/bridge`；
- 控制器侧可选择：1) 使用现有的 `app/controller/main.py --transport http`，通过场景文件循环推送；2) 或直接运行 `python -m app.controller.http_sim`，实时生成状态/切削/日志数据，并自动处理控制命令；
- 所有日志最终都会写入 `app.server.utils.logs` 的环形缓冲；WebSocket `/ws/logs` 会从该缓冲推送历史与增量，保证 UI 能实时看到 HTTP 模式下的日志。

> 小提示：通过环境变量 `COPPER_HTTP_BRIDGE_BASE`、`COPPER_HTTP_CONTROL`、`COPPER_HTTP_TIMEOUT` 可以自定义桥接地址、控制端点和超时时间。
