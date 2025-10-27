# CopperSystem 接口规范 / API Specification

- Base URL: `http://<host>:<port>` (default `127.0.0.1:8010`)
- WebSocket: `ws://<host>:<port>/ws` (status push every 500 ms)
- Responses are UTF-8 JSON unless noted (e.g., `/image.png` returns `image/png`).

## Authentication / 认证
The demo deployment has no authentication. Add ACLs or reverse-proxy auth when exposed outside the lab.

## Health Check / 健康检查
`GET /health` → `200 { "status": "ok" }`

## Video Frame / 视频图像
`GET /image.png`
- Returns the latest camera frame as PNG. When no camera is present, a 640×360 placeholder is served.
- Response type: `image/png`

## System Status / 系统状态
`GET /status`

```json
{
  "state": "IDLE|READY|MOVE|...",
  "position": { "x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0 },
  "spindle_rpm": 0
}
```

## Run Control / 运行控制
- `POST /run/start` → set status to READY (placeholder implementation)
- `POST /run/stop`  → set status to IDLE (placeholder implementation)
- Both return `{ "ok": true }`

## Motion Control / 运动控制
- `POST /motion/set_speed` with `{ "v_fast": 100.0, "v_work": 10.0 }`
- `POST /motion/jog` with `{ "axis": "x|y|z|t", "direction": ±1, "speed": 10.0 }`
- `POST /motion/home`
- `POST /motion/set_work_origin`

Each endpoint returns `{ "ok": true }` when successful.

## UI Launcher / UI 启动
`POST /ui/start`
- Starts the UI as a subprocess on the server, or returns the current status when it is already running.
- Responses:
  - `200 { "ok": true, "running": true }`
  - `500 { "ok": false, "error": "..." }`

## WebSocket
`WS /ws`
- Pushes the same payload as `/status` roughly every 500 ms.
- Clients should handle reconnects and backoff.

---

# OpenAPI
The generated OpenAPI contract resides in `docs/export/openapi.yaml`.
