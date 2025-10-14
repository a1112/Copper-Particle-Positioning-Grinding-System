from __future__ import annotations

import math
import random
import time
from typing import Protocol, Dict, Any, Optional


class IDataProvider(Protocol):
    def get_status(self) -> Dict[str, Any]:
        ...


class SimDataProvider:
    """Pure-simulated data provider for UI/API without real devices."""
    def __init__(self) -> None:
        self._t0 = time.monotonic()

    def get_status(self) -> Dict[str, Any]:
        # Simulate a smooth RPM/torque signal and a fixed pose
        t = time.monotonic() - self._t0
        rpm = 1500.0 + 600.0 * math.sin(2.0 * math.pi * 0.15 * t) + 120.0 * math.sin(2.0 * math.pi * 1.1 * t)
        torque = 0.6 + 0.25 * math.sin(2.0 * math.pi * 0.22 * t + 1.3) + 0.04 * math.sin(2.0 * math.pi * 1.8 * t)
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


class CommDataProvider:
    """Placeholder for real comms adapter. Replace with fieldbus/device RPC calls.

    For now returns static-ish values to satisfy UI expectations.
    """
    def __init__(self, endpoint: Optional[str] = None) -> None:
        self._endpoint = endpoint or "local"

    def get_status(self) -> Dict[str, Any]:
        # In the future, poll your comms channel here.
        base = 1200.0 + random.random() * 50.0
        return {
            "state": "IDLE",
            "position": {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0},
            "spindle_rpm": int(base),
            "spindle_torque": 0.5,
            "seriesA": base,
            "seriesB": 0.5,
        }


_current_provider: IDataProvider = SimDataProvider()


def set_provider(p: IDataProvider) -> None:
    global _current_provider
    _current_provider = p


def get_provider() -> IDataProvider:
    return _current_provider
