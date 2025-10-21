from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, Dict, Any

from starlette.websockets import WebSocket, WebSocketDisconnect

from ..api_core import ws_router
from app.server.data import get_backend

log = logging.getLogger("app.ws")


async def _default_status_fn() -> Dict[str, Any]:
    """从当前后端实现中读取最新状态，转换成字典返回。"""
    backend = get_backend()
    status_model = await backend.fetch_status()
    return status_model.to_dict()


status_fn: Callable[[], Awaitable[Dict[str, Any]]] = _default_status_fn


@ws_router.websocket("/ws/status")
async def ws_status(ws: WebSocket):
    """状态 WebSocket 入口：定期推送设备状态给前端。"""
    await ws.accept()
    try:
        try:
            log.info("WS connected endpoint=/ws client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        while True:
            payload = await status_fn()
            await ws.send_json(payload)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        try:
            log.info("WS disconnected endpoint=/ws client=%s", getattr(ws, "client", None))
        except Exception:
            pass
        return
