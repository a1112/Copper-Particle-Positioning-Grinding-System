from dataclasses import dataclass

@dataclass
class MovePlan:
    x: float
    y: float
    z: float = 0.0
    theta: float = 0.0
