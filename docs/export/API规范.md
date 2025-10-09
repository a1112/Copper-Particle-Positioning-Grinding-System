# CopperSystem 接口规范

- 基础地址：`http://<host>:<port>`（默认：`127.0.0.1:8010`）。
- WebSocket：`ws://<host>:<port>/ws`（状态推送，每 500ms 一次）。
- 返回体均为 UTF-8 编码的 JSON，除 `/image.png` 返回 `image/png`。

## 认证
- 当前接口无鉴权，建议在部署时加反向代理与访问控制。

## 健康检查
- GET `/health`
  - 200 响应：`{ "status": "ok" }`

## 视频帧
- GET `/image.png`
  - 说明：返回当前帧 PNG 图片；若无图像，返回默认 640x360 深灰背景。
  - 200 响应：`image/png`

## 系统状态
- GET `/status`
  - 200 响应体：
    ```json
    {
      "state": "IDLE|READY|MOVE|...",
      "position": { "x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0 },
      "spindle_rpm": 0
    }
    ```

## 运行控制
- POST `/run/start`
  - 说明：将状态置为 READY（占位实现）。
  - 200：`{ "ok": true }`
- POST `/run/stop`
  - 说明：将状态置为 IDLE（占位实现）。
  - 200：`{ "ok": true }`

## 运动控制
- POST `/motion/set_speed`
  - 请求体（JSON）：
    ```json
    { "v_fast": 100.0, "v_work": 10.0 }
    ```
  - 200：`{ "ok": true }`
- POST `/motion/jog`
  - 请求体（JSON）：
    ```json
    { "axis": "x", "direction": 1, "speed": 10.0 }
    ```
  - 说明：`axis` 取值 `x|y|z|t`，`direction` 取 `1|-1`。
  - 200：`{ "ok": true }`
- POST `/motion/home`
  - 200：`{ "ok": true }`
- POST `/motion/set_work_origin`
  - 200：`{ "ok": true }`

## UI 启动
- POST `/ui/start`
  - 说明：在服务器上以子进程启动 UI（若已运行则直接返回 running=true）。
  - 200：`{ "ok": true, "running": true }`
  - 500：`{ "ok": false, "error": "..." }`

## WebSocket 状态推送
- WS `/ws`
  - 说明：每 500ms 推送一次与 `/status` 相同结构的 JSON。
  - 客户端应处理网络中断与重连。

---

# OpenAPI 概览
- 完整的 OpenAPI 见同目录 `openapi.yaml`。

