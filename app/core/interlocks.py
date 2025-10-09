from typing import Protocol

class InterlockProvider(Protocol):
    def door_closed(self) -> bool: ...
    def vacuum_ok(self) -> bool: ...
    def spindle_ready(self) -> bool: ...

class Interlocks:
    def __init__(self, provider: InterlockProvider):
        self.p = provider

    def check_before_move(self) -> bool:
        return self.p.door_closed() and self.p.vacuum_ok()

    def check_before_grind(self) -> bool:
        return self.check_before_move() and self.p.spindle_ready()
