"""Simulated status provider for UI/API without real hardware."""

from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Tuple

from ..interfaces import StatusProviderProtocol


class SimStatusProvider(StatusProviderProtocol):
    """Pure-simulated provider that generates smooth test signals."""

    def __init__(self) -> None:
        self._t0 = time.monotonic()
        self._profile_base: float = 0.0
        self._profile_points: List[Tuple[float, float]] = self._build_profile_points()
        self._profile_cuts: List[Dict[str, float]] = [
            {"s": 8.0, "z": -0.28, "amount": 0.2},
            {"s": 22.0, "z": -0.46, "amount": 0.35},
            {"s": 47.0, "z": -0.62, "amount": 0.42},
            {"s": 73.0, "z": -0.38, "amount": 0.22},
            {"s": 95.0, "z": -0.58, "amount": 0.3},
        ]
        self._extra_status: Dict[str, Any] = {}

    def _build_profile_points(self) -> List[Tuple[float, float]]:
        """Construct a periodic 2D elevation curve that mimics grinding terrain."""
        steps = 96
        points: List[Tuple[float, float]] = []
        for i in range(steps + 1):
            s = float(i) * (100.0 / steps)
            z = -0.25 - 0.55 * math.sin(i / 8.5) - 0.08 * math.sin(i / 2.3 + 1.1)
            points.append((round(s, 3), round(z, 4)))
        return points

    def get_status(self) -> Dict[str, Any]:
        """Return a simulated status snapshot consumed by UI/API polling."""
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
        machine_state = "RUNNING" if rpm > 800 else ("PAUSED" if rpm > 200 else "IDLE")

        spindle_state = "RUNNING" if rpm > 600 else ("READY" if rpm > 100 else "STOP")
        camera_state = "READY" if math.sin(0.18 * t) >= -0.45 else "FAULT"
        device_state = (
            "RUNNING"
            if math.sin(0.1 * t + 1.2) > -0.15
            else ("WARNING" if math.sin(0.45 * t) > -0.2 else "IDLE")
        )
        interlock_ok = math.cos(0.24 * t) > -0.35
        lights: Dict[str, Any] = {
            "camera": camera_state,
            "spindle": spindle_state,
            "device": device_state,
            "interlock": interlock_ok,
            "server": True,
        }

        wobble_phase = 0.08 * math.sin(0.27 * t)
        points_payload = [
            {"s": s, "z": round(z + wobble_phase * math.sin(0.13 * s + 0.8), 4)}
            for s, z in self._profile_points
        ]
        cuts_payload: List[Dict[str, float]] = []
        for idx, cut in enumerate(self._profile_cuts):
            wobble = 0.04 * math.sin(0.55 * t + idx)
            cuts_payload.append(
                {
                    "s": cut["s"],
                    "z": round(cut["z"] + wobble, 3),
                    "amount": cut["amount"],
                }
            )
        profile_payload = {
            "base": self._profile_base,
            "points": points_payload,
            "cuts": cuts_payload,
        }

        return {
            "state": machine_state,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0},
            "spindle_rpm": int(rpm),
            "spindle_torque": round(torque, 3),
            "seriesA": rpm,
            "seriesB": torque,
            "statusLights": lights,
            "lightStates": lights,
            "lights": lights,
            "elevationProfile": profile_payload,
            "path_elevation": profile_payload,
            **self._extra_status,
        }

    def update_extra_status(self, **fields: Any) -> None:
        """Attach additional simulated metrics that should surface in responses."""
        self._extra_status.update(fields)
