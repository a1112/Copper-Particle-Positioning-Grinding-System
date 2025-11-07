from __future__ import annotations

import logging
import os
import threading
import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from app.devices.motion_base import IMotionController
from app.devices.procon.controller import ProConController, ProConDllError

__all__ = ["RuntimeMotion"]

_LOGGER = logging.getLogger(__name__)


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _normalize_axis_name(axis: str) -> str:
    key = str(axis or "").strip().lower()
    if key in {"theta", "t", "r"}:
        return "theta"
    return key


def _parse_axis_mapping(text: Optional[str]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    if not text:
        return mapping
    entries = text.split(",")
    for entry in entries:
        if ":" not in entry:
            continue
        axis_name, index_text = entry.split(":", 1)
        axis_key = _normalize_axis_name(axis_name)
        if not axis_key:
            continue
        try:
            mapping[axis_key] = int(index_text)
        except ValueError:
            continue
    return mapping


_DEFAULT_AXIS_MAP: Dict[str, int] = {"x": 0, "y": 1}
_AXIS_MAP = {**_DEFAULT_AXIS_MAP, **_parse_axis_mapping(os.getenv("COPPER_MOTION_AXIS_MAP"))}
_AXIS_ORDER: Sequence[str] = ("x", "y", "z", "theta")

_PROCON_IP = os.getenv("COPPER_PROCON_IP")
_PROCON_PORT = _env_int("COPPER_PROCON_PORT", 6000)
_DEFAULT_FAST = _env_float("COPPER_MOTION_V_FAST", 80.0)
_DEFAULT_WORK = _env_float("COPPER_MOTION_V_WORK", 10.0)
_DEFAULT_ACCEL = _env_float("COPPER_MOTION_ACCEL", 200.0)
_DEFAULT_DECEL = _env_float("COPPER_MOTION_DECEL", 200.0)
_DEFAULT_JERK = _env_float("COPPER_MOTION_JERK", 2000.0)
_DEFAULT_JOG_SECONDS = max(_env_float("COPPER_JOG_STEP_SECONDS", 0.15), 0.02)
_DEFAULT_JOG_MIN_STEP = max(_env_float("COPPER_JOG_MIN_STEP", 0.01), 0.001)


class RuntimeMotion(IMotionController):
    """Runtime motion controller backed by the ProCon DLL."""

    def __init__(self) -> None:
        self._controller = ProConController()
        self._lock = threading.RLock()
        self._axis_map: Dict[str, int] = dict(_AXIS_MAP)
        self._work_offsets: Dict[str, float] = {name: 0.0 for name in _AXIS_ORDER}
        self._speed_fast = _DEFAULT_FAST
        self._speed_work = _DEFAULT_WORK
        self._acceleration = _DEFAULT_ACCEL
        self._deceleration = _DEFAULT_DECEL
        self._jerk = _DEFAULT_JERK
        self._jog_duration = _DEFAULT_JOG_SECONDS
        self._min_jog_distance = _DEFAULT_JOG_MIN_STEP
        self._last_axes: List[int] = []
        self._connect()

    # ------------------------------------------------------------------ #
    # IMotionController API

    def home(self) -> None:
        """Soft-home by treating the current position as the new work origin."""
        self.set_work_origin()

    def move_abs(self, x: float, y: float, z: float = 0.0, theta: float = 0.0) -> None:
        targets = {"x": x, "y": y, "z": z, "theta": theta}
        commands: List[Tuple[int, float]] = []
        with self._lock:
            for axis_name, value in targets.items():
                axis_key = _normalize_axis_name(axis_name)
                if axis_key not in self._axis_map:
                    continue
                absolute = self._work_offsets.get(axis_key, 0.0) + float(value)
                commands.append((self._axis_map[axis_key], absolute))

            if not commands:
                return

            pending_axes: List[int] = []
            for axis_index, position in commands:
                self._ensure_axis_ready(axis_index)
                self._controller.move_absolute(
                    axis_index,
                    position=position,
                    velocity=self._speed_fast,
                    acceleration=self._acceleration,
                    deceleration=self._deceleration,
                    jerk_acc=self._jerk,
                    jerk_dec=self._jerk,
                    wait=False,
                )
                pending_axes.append(axis_index)

            self._last_axes = pending_axes

    def wait_done(self, timeout: float = 10.0) -> bool:
        deadline = time.time() + timeout
        axes = list(self._last_axes)
        for axis in axes:
            remaining = deadline - time.time()
            if remaining <= 0:
                return False
            self._controller.wait_axis_done(axis, timeout=remaining)
        return True

    def status(self) -> Tuple[float, float, float, float]:
        readings: List[float] = []
        with self._lock:
            for axis_name in _AXIS_ORDER:
                idx = self._axis_map.get(axis_name)
                if idx is None:
                    readings.append(0.0)
                    continue
                position = self._controller.read_axis_position(idx)
                readings.append(position - self._work_offsets.get(axis_name, 0.0))
        return tuple(readings)

    def set_soft_limits(self, xmin: float, xmax: float, ymin: float, ymax: float) -> None:
        with self._lock:
            if "x" in self._axis_map:
                self._controller.set_axis_soft_limit(
                    self._axis_map["x"],
                    positive=float(xmax),
                    negative=float(xmin),
                )
            if "y" in self._axis_map:
                self._controller.set_axis_soft_limit(
                    self._axis_map["y"],
                    positive=float(ymax),
                    negative=float(ymin),
                )

    def set_speed(self, v_fast: float, v_work: float) -> None:
        with self._lock:
            self._speed_fast = max(float(v_fast), 0.1)
            self._speed_work = max(float(v_work), 0.1)

    def jog(self, axis: str, direction: int, speed: float) -> None:
        axis_key = _normalize_axis_name(axis)
        if axis_key not in self._axis_map:
            raise ValueError(f"Unknown jog axis '{axis}'")
        axis_index = self._axis_map[axis_key]
        distance = max(abs(float(speed)) * self._jog_duration, self._min_jog_distance)
        if direction < 0:
            distance = -distance
        with self._lock:
            self._ensure_axis_ready(axis_index)
            self._controller.move_relative(
                axis_index,
                distance=distance,
                velocity=self._speed_work,
                acceleration=self._acceleration,
                deceleration=self._deceleration,
                jerk_acc=self._jerk,
                jerk_dec=self._jerk,
                wait=True,
            )
            self._last_axes = [axis_index]

    def set_work_origin(self) -> None:
        with self._lock:
            for axis_name, axis_index in self._iter_axes():
                self._work_offsets[axis_name] = self._controller.read_axis_position(axis_index)

    # ------------------------------------------------------------------ #
    # Internal helpers

    def _connect(self) -> None:
        kwargs = {}
        if _PROCON_IP:
            kwargs["ip"] = _PROCON_IP
            kwargs["port"] = _PROCON_PORT
        self._controller.load(**kwargs)
        self._controller.wait_bus_ready()
        for axis_index in self._axis_map.values():
            try:
                self._controller.clear_axis_error(axis_index)
                self._controller.power_on(axis_index)
            except ProConDllError as exc:
                _LOGGER.warning("Axis %s failed to power on: %s", axis_index, exc)

    def _iter_axes(self) -> Iterable[Tuple[str, int]]:
        for name, index in self._axis_map.items():
            if name not in _AXIS_ORDER:
                continue
            yield name, index

    def _ensure_axis_ready(self, axis_index: int) -> None:
        self._controller.clear_axis_error(axis_index)
        self._controller.power_on(axis_index)

    def __del__(self) -> None:
        try:
            self._controller.unload()
        except Exception:
            pass
