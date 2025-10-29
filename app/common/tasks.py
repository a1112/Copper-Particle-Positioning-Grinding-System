from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import IntEnum
from typing import Dict


class TaskType(IntEnum):
    """Supported high-level task categories persisted in hardware_task_queue."""

    CAPTURE = 10
    EXECUTE = 20
    CONTROL = 30


class TaskStatus(IntEnum):
    """Normalized task status values stored in hardware_task_queue."""

    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3


READY_STATES = frozenset({
    "READY",
    "设备准备就绪",
    "执行准备就绪",
    "重新识别",
    "IDLE",
})


@dataclass(slots=True)
class ControlInstruction:
    """Structured control command derived from algorithm outputs."""

    ex: float
    ey: float
    ez: float
    spindle_rpm: float
    velocity: float

    def as_dict(self) -> Dict[str, float]:
        return asdict(self)

    def as_command_string(self) -> str:
        return f"EX{self.ex:.3f} EY{self.ey:.3f} EZ{self.ez:.3f} R{self.spindle_rpm:.1f} V{self.velocity:.1f}"


__all__ = [
    "TaskType",
    "TaskStatus",
    "READY_STATES",
    "ControlInstruction",
]
