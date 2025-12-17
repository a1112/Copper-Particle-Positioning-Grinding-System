from __future__ import annotations

import threading
from collections import deque
from typing import Any, Deque, Dict, Iterable, Mapping


class HttpDataStore:
    """Thread-safe store keeping the latest snapshots pushed via HTTP bridge."""

    def __init__(self, *, log_capacity: int = 1500) -> None:
        self._status: Dict[str, Any] = {}
        self._cutting: Dict[str, Any] = {}
        self._program: list[str] = []
        self._program_state: Dict[str, Any] = {}
        self._logs: Deque[Dict[str, Any]] = deque(maxlen=max(log_capacity, 1))
        self._lock = threading.RLock()

    def update_status(self, payload: Mapping[str, Any]) -> None:
        with self._lock:
            self._status = dict(payload or {})

    def update_cutting(self, payload: Mapping[str, Any]) -> None:
        with self._lock:
            self._cutting = dict(payload or {})

    def append_log(self, entry: Mapping[str, Any]) -> None:
        with self._lock:
            self._logs.append(dict(entry or {}))

    def extend_logs(self, entries: Iterable[Mapping[str, Any]]) -> None:
        with self._lock:
            for entry in entries:
                self._logs.append(dict(entry or {}))

    def set_program(self, lines: Iterable[str]) -> None:
        with self._lock:
            self._program = [str(line) for line in lines]

    def set_program_state(self, state: Mapping[str, Any]) -> None:
        with self._lock:
            self._program_state = dict(state or {})

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._status)

    def get_cutting(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._cutting)

    def get_program(self) -> list[str]:
        with self._lock:
            return list(self._program)

    def get_program_state(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._program_state)

    def get_logs(self) -> Iterable[Dict[str, Any]]:
        with self._lock:
            return list(self._logs)

    def clear(self) -> None:
        with self._lock:
            self._status.clear()
            self._cutting.clear()
            self._logs.clear()
            self._program.clear()
            self._program_state.clear()


class HttpStatusProvider:
    """Status provider that proxies data from :class:`HttpDataStore`."""

    def __init__(self, store: HttpDataStore) -> None:
        self._store = store

    def get_status(self) -> Dict[str, Any]:
        return self._store.get_status()
