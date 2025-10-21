"""Production-oriented status provider hooking real comms."""

from __future__ import annotations

import random
import math
from typing import Any, Dict, Optional

from ..interfaces import StatusProviderProtocol


class ProductionStatusProvider(StatusProviderProtocol):
  """Placeholder provider; replace with real device/fieldbus integration."""

  def __init__(self, endpoint: Optional[str] = None) -> None:
    """记录设备通信端点，方便未来接入真实产线。"""
    self._endpoint = endpoint or "local"

  def get_status(self) -> Dict[str, Any]:
    """返回一帧静态的设备状态，模拟现场数据结构。"""
    base = 1200.0 + random.random() * 50.0
    lights: Dict[str, Any] = {
        "camera": "READY",
        "spindle": "RUNNING" if base > 1210 else "READY",
        "device": "RUNNING",
        "interlock": True,
        "server": True,
    }
    points = [
        {"s": round(i * 2.0, 3), "z": round(-0.28 - 0.42 * math.sin(i / 6.5), 4)}
        for i in range(0, 51)
    ]
    profile_payload = {
        "base": 0.0,
        "points": points,
        "cuts": [
            {"s": 12.0, "z": -0.32, "amount": 0.2},
            {"s": 38.0, "z": -0.5, "amount": 0.35},
            {"s": 74.0, "z": -0.41, "amount": 0.25},
        ],
    }
    return {
        "state": "IDLE",
        "position": {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0},
        "spindle_rpm": int(base),
        "spindle_torque": 0.5,
        "seriesA": base,
        "seriesB": 0.5,
        "statusLights": lights,
        "lightStates": lights,
        "lights": lights,
        "elevationProfile": profile_payload,
        "path_elevation": profile_payload,
    }
