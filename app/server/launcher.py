from __future__ import annotations

import threading
from typing import Optional

import uvicorn

from app.server import CONFIG


class ApiController:
    """Start/stop a uvicorn server in a background thread with restart capability."""

    def __init__(self) -> None:
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None

    def _run(self, app, host: str, port: int, log_level: str) -> None:
        config = uvicorn.Config(app=app, host=host, port=port, log_level=log_level)
        server = uvicorn.Server(config)
        self._server = server
        server.run()

    def start(self, app, port: Optional[int] = None) -> None:
        host = getattr(CONFIG, "app_host", "127.0.0.1")
        log_level = getattr(CONFIG, "log_level", "info")
        port = int(port or getattr(CONFIG, "app_port", 8000))
        self.stop()
        t = threading.Thread(target=self._run, args=(app, host, port, log_level), daemon=True)
        t.start()
        self._thread = t

    def stop(self) -> None:
        if self._server is not None:
            try:
                self._server.should_exit = True
            except Exception:
                pass
        if self._thread is not None and self._thread.is_alive():
            try:
                self._thread.join(timeout=1.5)
            except Exception:
                pass
        self._server = None
        self._thread = None

    def restart(self, app, port: Optional[int] = None) -> None:
        self.stop()
        self.start(app, port)

