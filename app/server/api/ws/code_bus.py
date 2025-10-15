from __future__ import annotations

import asyncio
from typing import Any, List


class CodeBus:
    """In-memory broadcaster for code program/state to all ws clients."""

    def __init__(self) -> None:
        self._subs: list[asyncio.Queue[dict]] = []
        self._program: list[str] = []
        self._lock = asyncio.Lock()

    def latest_program(self) -> list[str]:
        return list(self._program)

    async def set_program(self, lines: list[str]) -> None:
        async with self._lock:
            self._program = list(lines)
        await self._broadcast({"type": "program", "lines": list(lines)})

    async def set_state(self, state: str, current: int = -1) -> None:
        await self._broadcast({"type": "state", "state": state, "current": current})

    async def _broadcast(self, msg: dict) -> None:
        # deliver to all queues non-blocking
        for q in list(self._subs):
            try:
                q.put_nowait(msg)
            except Exception:
                try:
                    self._subs.remove(q)
                except Exception:
                    pass

    def subscribe(self) -> asyncio.Queue[dict]:
        q: asyncio.Queue[dict] = asyncio.Queue(maxsize=64)
        self._subs.append(q)
        return q


bus = CodeBus()

