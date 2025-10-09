from typing import Any, Dict
from dataclasses import dataclass, field

@dataclass
class Recipe:
    name: str
    locate: Dict[str, Any]
    move: Dict[str, Any]
    grind: Dict[str, Any]
    inspect: Dict[str, Any]
    error_policy: Dict[str, Any]
    # New sections from docs
    comm: Dict[str, Any] = field(default_factory=dict)       # host/port/timeout/retries
    safety: Dict[str, Any] = field(default_factory=dict)     # door/vacuum/e_stop/homed/spindle_ready
    coords: Dict[str, Any] = field(default_factory=dict)     # origins/transforms
