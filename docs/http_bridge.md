# HTTP 网桥说明

`HttpBusinessService` 提供基于 FastAPI 的轻量级网桥，用于在 API 进程与独立主控进程之间同步状态、切削数据以及日志。

- API 侧会自动挂载 `/bridge/status`、`/bridge/cutting`、`/bridge/logs`、`/bridge/ping` 等路由接收主控推送的数据，并写入线程安全的 `HttpDataStore`。
- 控制指令通过 `HttpControlClient` 向主控进程暴露的 `/control` 端点发送，主控进程在内部注册的回调会返回处理结果。
- 将环境变量 `COPPER_DATA_MODE=http`（或命令行参数选择 `--transport http`）即可启用 HTTP 网桥模式。
- `app/controller/main.py` 现已支持 `--transport http`，并会在本地启动一个 FastAPI 控制端点（默认 `http://127.0.0.1:9001/control`），同时定时向 API 的 `/bridge/*` 路由推送场景数据。
- 新增的 `HttpBusinessService` 会作为 API 层的 `BusinessService` 注入，供前端 WebSocket 与 REST 接口读取最新的状态与日志。

