# Copper Grinding System API Reference

本文件梳理 FastAPI 服务暴露的主要 HTTP / WebSocket 接口，便于 UI、主控程序以及第三方脚本共用。默认基础地址为：

- REST：`http://<host>:<port>/api`
- WebSocket：`ws://<host>:<port>/ws`

除 `/status/test_payload` 与 `/cutting/test_payload` 外均不需要认证。调试过程中可使用 `curl`、Postman 或项目内的主控脚本（`python -m app.controller.main`）。

> **延伸阅读**  
> - 模拟数据注入接口详见 [docs/api_test_payload.md](api_test_payload.md)。  
> - UI 所依赖的字段对照表详见 [docs/ui_data_contracts.md](ui_data_contracts.md)。

---

## 1. 状态 & 监控

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/status` | 返回当前 `StatusModel`（设备状态、位置、主轴信息等）。 |
| `GET` | `/status/health` | 健康检查，返回 `{ "status": "ok" }`。 |
| `GET` | `/status/delay` | 用于调试的固定延时接口，默认返回 `0`。 |
| `GET` | `/status/` | 根路径，当前返回示例数据。 |
| `POST`/`GET`/`DELETE` | `/status/test_payload` | 写入/查询/清除状态覆盖，用于模拟（详见专门文档）。 |

**响应示例**

```json
{
  "state": "RUNNING",
  "position": { "x": 125.4, "y": 42.8, "z": -0.46, "theta": 0.75 },
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

---

## 2. 切削数据

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/cutting` | 返回当前切削快照（进给、切削量、扭矩等，见下表）。 |
| `POST`/`GET`/`DELETE` | `/cutting/test_payload` | 写入/查询/清除切削覆盖，用于模拟。 |

**响应示例**

```json
{
  "ts": 1730000000.0,
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

---

## 3. 控制指令

| 方法 | 路径 | 请求体 | 说明 |
| ---- | ---- | ------ | ---- |
| `POST` | `/control/estop` | 无 | 触发急停。 |
| `POST` | `/control/reset` | 无 | 复位报警。 |
| `POST` | `/control/stop` | 无 | 停止当前流程。 |

返回值格式：

```json
{ "ok": true, "message": "...", "details": { ... } }
```

若下层执行失败，会返回 `HTTP 500`，内容同上但 `ok: false`。

---

## 4. 运动控制

| 方法 | 路径 | 请求体 | 说明 |
| ---- | ---- | ------ | ---- |
| `POST` | `/motion/set_speed` | `{ "v_fast": float, "v_work": float }` | 设置快移/工进速度。 |
| `POST` | `/motion/jog` | `{ "axis": "x|y|z|theta", "direction": int, "speed": float }` | 点动指定轴，`direction` 通常为 `±1`。 |
| `POST` | `/motion/home` | 无 | 执行回零。 |
| `POST` | `/motion/set_work_origin` | 无 | 设置工件原点。 |

所有接口成功时均返回 `{ "ok": true }`。

---

## 5. 配置 & 元数据

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/config/meta` | 返回从文档/配置中提取的机台元数据（序列号、刀具参数等），字段为最佳匹配结果。 |
| `GET` | `/config/settings` | 返回配置集合（包括 `tool_table` 等），由 `ConfigSettingsLoader` 负责加载。 |

示例（截取）：

```json
{
  "board_serial": "SIM-BOARD-01",
  "cutter_diameter": "80mm",
  "tool_life": "4h",
  "particle_count": "512"
}
```

---

## 6. 图像 & 轨迹

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/image.png` | 返回当前相机帧（PNG），若无相机则提供灰度占位图。 |
| `GET` | `/path/elevation` | 返回模拟的路径高度曲线 `{ base, points[], cuts[] }`。 |
| `POST` | `/path/plan` | 生成测试高度图与刀路，参数见下文，返回摘要并将 G-code 推送到 `/ws/code`。 |

`/path/plan` 支持以下查询参数（均可选）：

| 参数 | 默认值 | 含义 |
| ---- | ------ | ---- |
| `mode` | `"discrete"` | 刀路模式：`discrete` 或 `concentrated`。 |
| `width` / `height` | `200` | 高度图像素尺寸。 |
| `pixel_mm` | `0.2` | 像素与毫米的比例。 |
| `blobs` | `25` | 模拟缺陷数量。 |
| `clustered_ratio` | `0.4` | 缺陷聚簇比例。 |

成功响应示例：

```json
{
  "ok": true,
  "mode": "discrete",
  "pixel_mm": 0.2,
  "summary": { "...": "..." },
  "program_lines": 420
}
```

---

## 7. WebSocket 通道

| 路径 | 载荷格式 | 说明 |
| ---- | -------- | ---- |
| `/ws/status` | 周期 JSON 快照 | 由 `BusinessService.fetch_status()` 提供，供 UI 实时刷新。 |
| `/ws/logs` | `{ "type": "history"|"append", ... }` | 先发送完整历史，再增量推送；无日志时会发送心跳。 |
| `/ws/code` | `{ "type": "program" | "state", ... }` | 推送 G-code 程序和执行状态，`/path/plan` 会写入。 |

所有 WebSocket 连接均采用 0.5s 轮询/心跳，无需额外认证。

---

## 8. 常见调试命令

```powershell
# 健康检查
curl http://127.0.0.1:8010/api/status/health

# 查看当前状态覆盖
curl http://127.0.0.1:8010/api/status/test_payload

# 注入状态（merge=false 覆盖）
curl -X POST http://127.0.0.1:8010/api/status/test_payload?merge=false ^
     -H "Content-Type: application/json" ^
     -d "{\"state\":\"RUNNING\",\"spindle_rpm\":2200}"

# 获取切削数据
curl http://127.0.0.1:8010/api/cutting
```

如需实时观察 WebSocket，可使用 `websocat` 或浏览器控制台：

```bash
websocat ws://127.0.0.1:8010/ws/status
```

---

## 9. 版本与兼容提示

- API 暂不做权限控制，若部署于生产环境，请在网关层添加认证。  
- 状态/切削字段兼容驼峰与下划线命名，详见 [UI 数据契约文档](ui_data_contracts.md)。  
- 当新增字段时，请同步更新：`docs/ui_data_contracts.md`、`StatusDatas.qml`、`DeviceInfoData.qml`，并考虑更新主控场景文件。  
- 若使用缓存/代理，请注意 `/status/test_payload` 等端点的短时写操作不会自动推送至客户端，必须靠 WebSocket 刷新才可见。*** End Patch
