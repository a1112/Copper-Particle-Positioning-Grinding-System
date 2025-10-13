from __future__ import annotations

import logging
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from typing import Deque, Dict, Any, List, Optional


_BUFFER: Deque[Dict[str, Any]] = deque(maxlen=1000)


class _BufferHandler(logging.Handler):
    def __init__(self, level: int = logging.INFO) -> None:
        super().__init__(level=level)
        self._is_ws_buffer = True  # marker to avoid duplicates

    def emit(self, record: logging.LogRecord) -> None:
        try:
            ts = getattr(record, "ts", None) or time.time()
            item = {
                "ts": ts,
                "time": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
                "level": record.levelname,
                "name": record.name,
                "msg": record.getMessage(),
            }
            _BUFFER.append(item)
        except Exception:
            # Never raise from log bus
            pass


def get_buffer() -> Deque[Dict[str, Any]]:
    return _BUFFER


def as_list() -> List[Dict[str, Any]]:
    return list(_BUFFER)


def push(level: str, name: str, msg: str, ts: Optional[float] = None) -> None:
    try:
        item = {"ts": ts or time.time(), "level": level.upper(), "name": name, "msg": msg}
        _BUFFER.append(item)
    except Exception:
        pass


def attach_root_handler(level: int = logging.INFO) -> None:
    """Attach root handlers once: in-memory buffer + daily rotating file.

    - Buffer handler feeds WS /ws/logs
    - File handler writes to logs/server, split by date
    """
    root = logging.getLogger()

    # Buffer handler for WS
    if not any(getattr(h, "_is_ws_buffer", False) for h in root.handlers):
        root.addHandler(_BufferHandler(level=level))

    # Timed rotating file handler (daily)
    if not any(getattr(h, "_is_server_file", False) for h in root.handlers):
        try:
            # Project root = .../app/api/utils -> parents[3]
            project_root = Path(__file__).resolve().parents[3]
            logs_dir = project_root / "logs" / "server"
            logs_dir.mkdir(parents=True, exist_ok=True)
            log_path = logs_dir / "server.log"

            fh = TimedRotatingFileHandler(
                filename=str(log_path),
                when="midnight",
                interval=1,
                backupCount=14,
                encoding="utf-8",
                utc=False,
            )
            # Ensure filename suffix by date
            fh.suffix = "%Y-%m-%d"
            fmt = logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            fh.setFormatter(fmt)
            fh.setLevel(level)
            fh._is_server_file = True  # type: ignore[attr-defined]
            root.addHandler(fh)
            # Keep root level high enough
            if root.level > level or root.level == logging.NOTSET:
                root.setLevel(level)
        except Exception:
            # File logging should not break app
            pass
