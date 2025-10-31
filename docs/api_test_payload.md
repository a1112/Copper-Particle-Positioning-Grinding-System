# 测试数据注入接口说明

UI 测试窗口与独立主控程序会通过下述 REST 接口向服务端写入“虚拟产线数据”，后端再统一推送给 WebSocket / HTTP 订阅者，驱动 UI 刷新。HTTP 网桥基于 FastAPI `/bridge/*` 路由接收状态与日志，主控可以选择 gRPC 或 HTTP 方式投递。所有端点均挂载在 FastAPI 的 `status_router`、`path_router` 下，默认基础地址为 `http://<host>:<port>/api`（参见 `app/server/run_api.py` 与 `CONFIG.app_host/app_port` 配置）。

---

## 1. 状态模拟接口 `/status/test_payload`

| 方法 | 说明 | 备注 |
| ---- | ---- | ---- |
| `POST` | 写入或合并状态快照 | 与 `/ws/status` 同步 |
| `GET`  | 查询当前手动覆盖数据 | 便于调试与确认 |
| `DELETE` | 清除覆盖（全部或部分字段） | 恢复默认模拟输出 |

### 1.1 `POST /status/test_payload`

- **Query 参数**：`merge`（可选，布尔）——`true` 表示与现有覆盖深度合并；默认 `false` 表示完全覆盖。
- **请求体**：任意 JSON 对象，会透传到 `StatusModel.to_dict()`。常见字段如下：

```json
{
  "state": "RUNNING",
  "run_mode": "AUTO",
  "serial_number": "SIM-0998",
  "position": { "x": 123.4, "y": 58.6, "z": -0.42, "theta": 1.2 },
  "spindle_rpm": 2350,
  "spindle_torque": 0.58,
  "feed_rate": 24.0,
  "statusLights": {
    "camera": "READY",
    "spindle": "RUNNING",
    "device": "RUNNING",
    "interlock": true,
    "server": true
  }
}
```

- **响应体**：

```json
{
  "overrides": { ... 合并完成后的字典 ... },
  "merge": false
}
```

### 1.2 `GET /status/test_payload`

返回当前仍生效的手动覆盖字典；若为 `{}` 表示已恢复默认模拟输出。

### 1.3 `DELETE /status/test_payload`

- **Query 参数**：`keys`（可选，逗号分隔字符串）——仅清除部分字段，例如 `keys=state,statusLights`。
- **响应体**：

```json
{
  "cleared": ["*"]      // 或具体字段名列表
}
```

---

## 2. 切削数据接口 `/cutting/test_payload`

切削数据供 `CuttingWork` 轮询 `/cutting` 后更新 `CuttingDatas`，驱动统计卡片与曲线图。

| 方法 | 说明 | 备注 |
| ---- | ---- | ---- |
| `POST` | 写入或合并切削指标 | 立即影响 `/api/cutting` 输出 |
| `GET`  | 查询当前覆盖 |  |
| `DELETE` | 清除覆盖 | 同时重置内部扭矩峰值 |

### 2.1 `POST /cutting/test_payload`

- **Query 参数**：`merge`（可选，布尔），与状态接口一致。
- **常用字段**：

```json
{
  "feed_rate": 24.0,
  "downfeed_target": 0.8,
  "downfeed_current": 0.58,
  "removal_current": 48.3,
  "removal_expected": 120.0,
  "torque": 0.55,
  "torque_max": 0.62,
  "elapsed_sec": 360
}
```

- **响应体**：

```json
{
  "overrides": { ... },
  "merge": false
}
```

### 2.2 `GET /cutting/test_payload`

返回当前覆盖的切削字段字典。

### 2.3 `DELETE /cutting/test_payload`

- **Query 参数**：`keys`（可选）。未指定或为空则清除所有字段并复位历史最大扭矩。
- **响应体**：

```json
{
  "cleared": ["*"]
}
```

---

## 3. 示例：通过主控程序推送场景

项目内置 `app/controller/sample_scenarios.json`，可通过以下命令循环推送（gRPC 模式）：

```powershell
python -m app.controller.main --scenario app/controller/sample_scenarios.json --loop
```

常用参数：

- `--interval` / `--respect-delay`：控制场景节奏。
- `--rpc-server`：API / gRPC 监听地址（默认读取 `app.config.RPC_LISTEN_ENDPOINT`）。
- `--rpc-listen`：主控自身接收控制命令的 gRPC 地址（默认读取 `app.config.RPC_CONTROL_ENDPOINT`）。
- `--rpc-timeout`：gRPC 调用超时时间。

---

## 4. 调试建议

1. **接口探测**：使用 `curl` 或 Postman 调用上述 REST 接口，快速验证字段是否生效。
2. **UI 监控**：在 UI F12 测试窗口的“测试数据注入”面板查看实时日志反馈。
3. **恢复默认**：需要回到纯模拟环境时，确认 `GET /status/test_payload` 与 `GET /cutting/test_payload` 均返回 `{}`。
