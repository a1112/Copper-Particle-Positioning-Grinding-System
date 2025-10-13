from __future__ import annotations

import logging
import time
from collections import deque
from typing import Deque, Dict, Any, List, Optional


_BUFFER: Deque[Dict[str, Any]] = deque(maxlen=1000)


class _BufferHandler(logging.Handler):
    def __init__(self, level: int = logging.INFO) -> None:
        super().__init__(level=level)
        self._is_ws_buffer = True  # marker to avoid duplicates

    def emit(self, record: logging.LogRecord) -> None:
        try:
            item = {
                "ts": getattr(record, "ts", None) or time.time(),
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
    """Attach a root logger handler once that mirrors logging records to buffer."""
    root = logging.getLogger()
    if any(getattr(h, "_is_ws_buffer", False) for h in root.handlers):
        return
    root.addHandler(_BufferHandler(level=level))

