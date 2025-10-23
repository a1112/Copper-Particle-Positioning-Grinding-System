from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Dict, Mapping, Optional

from fastapi import FastAPI
import uvicorn

log = logging.getLogger("controller.httpbridge.server")

ControlCallback = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


class HttpControllerServer:
    """Simple FastAPI server that receives control commands from the API."""

    def __init__(self, *, host: str, port: int, callback: ControlCallback) -> None:
        self._host = host
        self._port = port
        self._callback = callback
        self._app = FastAPI(title="Controller Control Bridge")
        self._app.add_api_route("/control", self._handle_control, methods=["POST"])
        self._app.add_api_route("/control", self._handle_ping, methods=["GET"])
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None

    async def _handle_control(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = str(payload.get("action", ""))
        params = payload.get("params")
        if not isinstance(params, Mapping):
            params = {}
        try:
            response = dict(self._callback(action, params))
        except Exception as exc:
            log.exception("Control handler failure for action=%s: %s", action, exc)
            return {"ok": False, "error": str(exc)}
        response.setdefault("ok", True)
        return response

    async def _handle_ping(self) -> Dict[str, Any]:
        return {"ok": True}

    def start(self) -> None:
        if self._server is not None:
            return
        config = uvicorn.Config(self._app, host=self._host, port=self._port, log_level="warning")
        server = uvicorn.Server(config)

        def _run() -> None:
            log.info("Controller HTTP control server listening at http://%s:%s/control", self._host, self._port)
            try:
                server.run()
            except Exception as exc:  # pragma: no cover - background guard
                log.error("Controller HTTP control server stopped unexpectedly: %s", exc)

        thread = threading.Thread(target=_run, name="controller-http-control", daemon=True)
        thread.start()
        self._server = server
        self._thread = thread

    def stop(self) -> None:
        server = self._server
        if server is None:
            return
        server.should_exit = True
        thread = self._thread
        self._server = None
        self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=2)

