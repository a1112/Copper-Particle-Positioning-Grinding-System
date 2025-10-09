from __future__ import annotations

import threading
from typing import Optional

import uvicorn


class ApiController:
    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[uvicorn.Server] = None
        self._port: int = 0

    def start(self, app, port: int) -> None:
        self.stop()
        config = uvicorn.Config(app, host="127.0.0.1", port=int(port), log_level="warning")
        server = uvicorn.Server(config)
        self._server = server
        self._port = int(port)

        def _run():
            try:
                server.run()
            finally:
                # mark stopped
                pass

        t = threading.Thread(target=_run, daemon=True)
        self._thread = t
        t.start()

    def stop(self) -> None:
        if self._server is not None:
            try:
                self._server.should_exit = True
            except Exception:
                pass
        if self._thread is not None:
            try:
                self._thread.join(timeout=2.0)
            except Exception:
                pass
        self._server = None
        self._thread = None

    def restart(self, app, port: int) -> None:
        self.stop()
        self.start(app, port)

    @property
    def port(self) -> int:
        return self._port

