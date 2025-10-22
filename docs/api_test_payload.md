# 测试数据注入接口说明

UI 测试窗口仍会通过下述 REST 接口把“虚拟产线数据”写入后端；独立主控程序 (`app/controller/main.py`) 则改为通过内置 ZeroRPC 网桥投递同样的内容，后端再统一向 WebSocket/HTTP 订阅者推送，从而驱动 UI 刷新。

所有路径均挂载在 FastAPI 的 `status_router`、`path_router` 下，默认基础地址为 `http://<host>:<port>/api`（参见 `app/server/run_api.py` 中 `CONFIG.app_host/app_port` 配置）。

---

## 1. 状态模拟接口 `/status/test_payload`

| 方法 | 说明 | 备注 |
| ---- | ---- | ---- |
| `POST` | 写入/合并状态快照 | 与状态 `WebSocket (/ws/status)` 同步 |
| `GET`  | 查询当前手动覆盖数据 | 便于调试和确认状态 |
| `DELETE` | 清除覆盖数据（全部或指定字段） | 还原为默认模拟器输出 |

### 1.1 `POST /status/test_payload`

- **Query 参数**
  - `merge` (可选，布尔) — `true` 时与现有覆盖做深度合并；默认 `false` 表示覆盖整个快照。
- **请求体**：任意 JSON 对象，字段会透传到 `StatusModel.to_dict()` 的结果中。常用字段如下：

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

- **响应体**

```json
{
  "overrides": { ... 与请求体合并后的实际覆盖内容 ... },
  "merge": false
}
```

### 1.2 `GET /status/test_payload`

返回当前仍在生效的手动覆盖字典；若为空对象 `{}` 表示已恢复为默认模拟输出。

### 1.3 `DELETE /status/test_payload`

- **Query 参数**
  - `keys` (可选，逗号分隔字符串) — 仅清除部分字段。例如 `keys=state,statusLights`。
- **响应体**

```json
{
  "cleared": ["*"]         // 或具体字段名列表
}
```

---

## 2. 切削数据接口 `/cutting/test_payload`

切削数据用于 `CuttingWork` 轮询 `/cutting` 接口后更新 `CuttingDatas`，从而驱动统计卡片、曲线图等组件。

| 方法 | 说明 | 备注 |
| ---- | ---- | ---- |
| `POST` | 写入/合并切削指标 | 会立即影响 `/api/cutting` 输出 |
| `GET`  | 查询当前覆盖 | |
| `DELETE` | 清除覆盖 | 同时重置内部扭矩峰值 |

### 2.1 `POST /cutting/test_payload`

- **Query 参数**
  - `merge` (可选，布尔) — 与状态接口相同，默认覆盖全部字段。
- **常用字段**

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

- **响应体**

```json
{
  "overrides": { ... },
  "merge": false
}
```

### 2.2 `GET /cutting/test_payload`

返回当前覆盖的切削字段字典。

### 2.3 `DELETE /cutting/test_payload`

- **Query 参数**
  - `keys` (可选) — 若未指定或为空，则清除全部字段并复位历史最大扭矩。
- **响应体**

```json
{
  "cleared": ["*"]
}
```

---

## 3. 示例：通过主控程序推送场景

项目内置示例场景文件 `app/controller/sample_scenarios.json`，可通过以下命令循环推送（ZeroRPC 模式）：

```powershell
python -m app.controller.main --scenario app/controller/sample_scenarios.json --loop
```

命令行参数说明：

- `--interval` / `--respect-delay`：控制场景播放节奏。
- `--rpc-server`：API 端 ZeroRPC 监听地址（默认读取 `app.config.RPC_LISTEN_ENDPOINT`）。
- `--rpc-listen`：主控自身用于接收控制命令的 ZeroRPC 地址（默认读取 `app.config.RPC_CONTROL_ENDPOINT`）。
- `--rpc-timeout`：ZeroRPC 调用超时时间。

---

## 4. 调试建议

1. **接口探测**：可使用 `curl` 或 Postman 直接调用上述 REST 接口，快速验证字段是否按预期生效。
2. **UI 监控**：打开 UI F12 测试窗口的“测试数据注入”面板即可实时查看日志反馈。
3. **恢复默认**：当需要回到纯模拟环境时，请确认 `GET /status/test_payload` 与 `GET /cutting/test_payload` 均返回 `{}`。
