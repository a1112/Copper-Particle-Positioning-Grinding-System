from enum import Enum, auto
from typing import Optional, Callable, Dict

class ProcState(Enum):
    IDLE = auto()
    CALIBRATING = auto()
    READY = auto()
    LOCATE = auto()
    MOVE = auto()
    PREGRIND = auto()
    GRIND = auto()
    INSPECT = auto()
    COMPLETE = auto()
    FAULT = auto()

class StateMachine:
    def __init__(self):
        self.state = ProcState.IDLE
        self.handlers: Dict[ProcState, Callable[[], None]] = {}

    def on(self, state: ProcState, func: Callable[[], None]):
        self.handlers[state] = func

    def step(self):
        h = self.handlers.get(self.state)
        if h:
            h()
