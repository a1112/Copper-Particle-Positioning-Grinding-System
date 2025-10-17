"""Production-oriented status provider hooking real comms."""

from __future__ import annotations

import random
from typing import Any, Dict, Optional

from ..interfaces import StatusProviderProtocol


class ProductionStatusProvider(StatusProviderProtocol):
  """Placeholder provider; replace with real device/fieldbus integration."""

  def __init__(self, endpoint: Optional[str] = None) -> None:
    self._endpoint = endpoint or "local"

  def get_status(self) -> Dict[str, Any]:
    base = 1200.0 + random.random() * 50.0
    return {
        "state": "IDLE",
        "position": {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0},
        "spindle_rpm": int(base),
        "spindle_torque": 0.5,
        "seriesA": base,
        "seriesB": 0.5,
    }
