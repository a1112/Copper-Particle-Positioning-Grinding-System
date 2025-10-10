from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Property, Signal, Slot
from app.config import DEBUG as _DEBUG_FLAG


class SettingsBridge(QObject):
    """设置桥（中文注释）

    读取/保存 UI 侧配置（API 主机与端口），并提供信号通知与重启钩子。
    """
    apiPortChanged = Signal()
    apiHostChanged = Signal()

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self._api_port = 8010
        self._api_host = "127.0.0.1"
        self._debug = bool(_DEBUG_FLAG)
        self.load()
        self._api_ctl = None

    def load(self) -> None:
        """加载配置文件（中文注释）。"""
        try:
            if self._path.exists():
                data: dict[str, Any] = json.loads(self._path.read_text(encoding="utf-8"))
                port = int(data.get("api_port", self._api_port))
                host = str(data.get("api_host", self._api_host))
                changed = False
                if port != self._api_port:
                    self._api_port = port
                    self.apiPortChanged.emit()
                    changed = True
                if host and host != self._api_host:
                    self._api_host = host
                    self.apiHostChanged.emit()
                    changed = True
        except Exception:
            pass

    @Slot()
    def save(self) -> None:
        """保存配置文件（中文注释）。"""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps({
                    "api_port": int(self._api_port),
                    "api_host": str(self._api_host),
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    @Slot()
    def saveAndRestart(self) -> None:
        """保存并触发 API 重启（中文注释）。"""
        self.save()
        try:
            if self._api_ctl is not None:
                # _api_ctl expects .restart(app, port); app needs to be pre-bound.
                self._api_ctl("restart", int(self._api_port))
        except Exception:
            pass

    @Property(int, notify=apiPortChanged)
    def apiPort(self) -> int:  # type: ignore[override]
        """API 端口（中文注释）。"""
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

    @Property(str, notify=apiHostChanged)
    def apiHost(self) -> str:  # type: ignore[override]
        """API 主机名/IP（中文注释）。"""
        return str(self._api_host)

    @apiHost.setter  # type: ignore[override]
    def apiHost(self, v: str) -> None:
        try:
            v = str(v).strip()
            if v and v != self._api_host:
                self._api_host = v
                self.apiHostChanged.emit()
        except Exception:
            pass

    # Debug flag (read-only; from env via app.config)
    @Property(bool, constant=True)
    def debugEnabled(self) -> bool:  # type: ignore[override]
        return bool(self._debug)

    # Attach a restart hook from the host app
    @Slot()
    def clearController(self) -> None:
        """清除已绑定的控制器钩子（中文注释）。"""
        self._api_ctl = None

    def bindController(self, hook) -> None:
        """绑定控制器钩子（中文注释）。

        约定：hook(action: str, port: int)
        """
        self._api_ctl = hook
