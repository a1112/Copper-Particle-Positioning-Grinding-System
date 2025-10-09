from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Property, Signal, Slot


class SettingsBridge(QObject):
    apiPortChanged = Signal()

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self._api_port = 8010
        self.load()
        self._api_ctl = None

    def load(self) -> None:
        try:
            if self._path.exists():
                data: dict[str, Any] = json.loads(self._path.read_text(encoding="utf-8"))
                port = int(data.get("api_port", self._api_port))
                if port != self._api_port:
                    self._api_port = port
                    self.apiPortChanged.emit()
        except Exception:
            pass

    @Slot()
    def save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps({"api_port": int(self._api_port)}, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    @Slot()
    def saveAndRestart(self) -> None:
        self.save()
        try:
            if self._api_ctl is not None:
                # _api_ctl expects .restart(app, port); app needs to be pre-bound.
                self._api_ctl("restart", int(self._api_port))
        except Exception:
            pass

    @Property(int, notify=apiPortChanged)
    def apiPort(self) -> int:  # type: ignore[override]
        return int(self._api_port)

    @apiPort.setter  # type: ignore[override]
    def apiPort(self, v: int) -> None:
        try:
            v = int(v)
            if v != self._api_port and 0 < v < 65536:
                self._api_port = v
                self.apiPortChanged.emit()
        except Exception:
            pass

    # Attach a restart hook from the host app
    @Slot()
    def clearController(self) -> None:
        self._api_ctl = None

    def bindController(self, hook) -> None:
        """Host app injects a simple callable: hook(action: str, port: int)"""
        self._api_ctl = hook
