"""Simulated status provider for UI/API without real hardware."""

from __future__ import annotations

import math
import time
from typing import Any, Dict

from ..interfaces import StatusProviderProtocol


class SimStatusProvider(StatusProviderProtocol):
  """Pure-simulated provider that generates smooth test signals."""

  def __init__(self) -> None:
    self._t0 = time.monotonic()

  def get_status(self) -> Dict[str, Any]:
    t = time.monotonic() - self._t0
    rpm = (
        1500.0
        + 600.0 * math.sin(2.0 * math.pi * 0.15 * t)
        + 120.0 * math.sin(2.0 * math.pi * 1.1 * t)
    )
    torque = (
        0.6
        + 0.25 * math.sin(2.0 * math.pi * 0.22 * t + 1.3)
        + 0.04 * math.sin(2.0 * math.pi * 1.8 * t)
    )
    rpm = max(0.0, rpm)
    torque = max(0.0, torque)
    return {
        "state": "IDLE",
        "position": {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0},
        "spindle_rpm": int(rpm),
        "spindle_torque": round(torque, 3),
        "seriesA": rpm,
        "seriesB": torque,
    }
