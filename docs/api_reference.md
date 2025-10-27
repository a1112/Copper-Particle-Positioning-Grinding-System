# Copper Grinding System API Reference

本文件整理了 FastAPI 服务当前开放的主要 HTTP / WebSocket 接口，方便 UI、主控程序以及运维脚本复用。除特别说明外，默认基础地址为：

- REST：`http://<host>:<port>/api`
- WebSocket：`ws://<host>:<port>/ws`

除 `/status/test_payload` 与 `/cutting/test_payload` 等测试端点外，其余接口均在内网环境免认证使用；如需部署到生产，请在网关层追加鉴权策略。

> **延伸阅读**  
> - 模拟数据注入流程见 [docs/api_test_payload.md](api_test_payload.md)  
> - UI 依赖字段对照见 [docs/ui_data_contracts.md](ui_data_contracts.md)

---

## 1. 状态与监控

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/status` | 返回 `StatusModel`（设备状态、位置、主轴、灯态等）|
| `GET` | `/status/health` | 健康检查，返回 `{ "status": "ok" }` |
| `GET` | `/status/delay` | 调试用的固定延时接口，默认延迟 `0` 秒 |
| `GET` | `/status/` | 根路径，返回示例状态 |
| `POST`/`GET`/`DELETE` | `/status/test_payload` | 写入 / 查询 / 清空状态覆盖，用于模拟（详见测试文档）|

**示例响应**

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

## 2. 刀具与设备信息

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/toolList` | 返回当前刀具列表（型号、直径、寿命等字段）|
| `GET` | `/devices` | 返回设备拓扑及实时状态（若开启）|

返回体均为 JSON 数组，字段与 `docs/ui_data_contracts.md` 中的 `ToolInfoData`、`DeviceInfoData` 一致。

---

## 3. 切削与工艺数据

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/cutting` | 返回当前切削快照（进给、切削量、扭矩等，见下方示例）|
| `POST`/`GET`/`DELETE` | `/cutting/test_payload` | 写入 / 查询 / 清空切削覆盖，用于模拟 |

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

## 4. 控制指令

| 方法 | 路径 | 请求体 | 说明 |
| ---- | ---- | ------ | ---- |
| `POST` | `/control/estop` | `{}` | 触发急停 |
| `POST` | `/control/reset` | `{}` | 复位报警 |
| `POST` | `/control/stop` | `{}` | 停止当前流程 |

成功时统一返回 `{ "ok": true, "message": "...", "details": { ... } }`。如下层执行失败，将返回 `HTTP 500`，并携带 `ok: false` 以及详细原因。

---

## 5. 运动控制

| 方法 | 路径 | 请求体 | 说明 |
| ---- | ---- | ------ | ---- |
| `POST` | `/motion/set_speed` | `{ "v_fast": float, "v_work": float }` | 设置快移/工进速度 |
| `POST` | `/motion/jog` | `{ "axis": "x|y|z|theta", "direction": int, "speed": float }` | 点动指定轴，`direction` 取 `±1` |
| `POST` | `/motion/home` | `{}` | 执行回零 |
| `POST` | `/motion/set_work_origin` | `{}` | 设置工件原点 |

所有运动接口成功时返回 `{ "ok": true }`。

---

## 6. 配置与元数据

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/config/meta` | 读取配置中的机台元数据（序列号、刀具参数等），字段为最佳匹配结果 |
| `GET` | `/config/settings` | 返回配置集合（包含 `tool_table` 等），由 `ConfigSettingsLoader` 负责解析 |

```json
{
  "board_serial": "SIM-BOARD-01",
  "cutter_diameter": "80mm",
  "tool_life": "4h",
  "particle_count": "512"
}
```

---

## 7. 图像与轨迹

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| `GET` | `/image.png` | 返回当前相机帧（PNG），若无相机则给出灰度占位图 |
| `GET` | `/path/elevation` | 返回模拟路径高度曲线 `{ base, points[], cuts[] }` |
| `POST` | `/path/plan` | 根据参数生成测试高度图与刀路，并将 G-code 推送到 `/ws/code` |

`/path/plan` 支持以下查询参数（均可选）：

| 参数 | 默认值 | 含义 |
| ---- | ------ | ---- |
| `mode` | `"discrete"` | 刀路模式：`discrete` 或 `concentrated` |
| `width` / `height` | `200` | 高度图像素尺寸 |
| `pixel_mm` | `0.2` | 像素与毫米的比例 |
| `blobs` | `25` | 模拟缺陷数量 |
| `clustered_ratio` | `0.4` | 缺陷聚簇比例 |

---

## 8. WebSocket 通道

| 路径 | 载荷格式 | 说明 |
| ---- | -------- | ---- |
| `/ws/status` | 周期 JSON 快照 | 来自 `BusinessService.fetch_status()`，用于 UI 实时刷新 |
| `/ws/logs` | `{ "type": "history"|"append", ... }` | 先推送完整历史，再推送增量；无日志时发送心跳 |
| `/ws/code` | `{ "type": "program" | "state", ... }` | 推送 G-code 程序及执行状态，`/path/plan` 会写入 |

所有通道默认 0.5 s 心跳间隔，无需额外认证。

---

## 9. 常用调试命令

```powershell
# 健康检查
curl http://127.0.0.1:8010/api/status/health

# 查看当前状态覆盖
curl http://127.0.0.1:8010/api/status/test_payload

# 注入状态（merge=false 表示覆盖）
curl -X POST "http://127.0.0.1:8010/api/status/test_payload?merge=false" ^
     -H "Content-Type: application/json" ^
     -d '{"state":"RUNNING","spindle_rpm":2200}'

# 获取切削数据
curl http://127.0.0.1:8010/api/cutting
```

如需实时观察 WebSocket，可使用 `websocat`、`wscat` 或浏览器控制台：

```bash
websocat ws://127.0.0.1:8010/ws/status
```

---

## 10. 版本与兼容提示

- API 暂未启用权限控制，生产部署请在反向代理或 Service Mesh 层添加认证。
- 状态/切削字段同时兼容驼峰与下划线命名，详见 [UI 数据契约](ui_data_contracts.md)。
- 若新增字段，请同步更新 `docs/ui_data_contracts.md`、`StatusDatas.qml`、`DeviceInfoData.qml` 以及相关业务逻辑。
- 如通过缓存代理访问，请注意 `/status/test_payload` 等端点为短期写操作，需依赖 WebSocket 才能实时看到更新。
