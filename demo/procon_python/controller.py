from __future__ import annotations

import ctypes
import importlib
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional, Sequence

__all__ = ["DigitalPoint", "ProConDllError", "ProConController"]


class ProConDllError(RuntimeError):
    """Raised when a ProCon SDK call fails."""


@dataclass(frozen=True)
class DigitalPoint:
    """Represents a digital IO point."""

    slave_id: int
    index: int


class ProConController:
    """High-level wrapper around the YKCat2 DLL used by GantryMilling."""

    def __init__(
        self,
        *,
        dll_dir: Optional[Path | str] = None,
        include_dir: Optional[Path | str] = None,
        node_name: str = "YKE_ECAT_A",
    ) -> None:
        if sys.platform != "win32":
            raise ProConDllError("The ProCon DLL is only supported on Windows.")

        base_dir = Path(__file__).resolve().parent
        self._dll_dir = Path(dll_dir or (base_dir / "dll")).resolve()
        self._include_dir = Path(include_dir or base_dir).resolve()
        self._node_name = node_name

        self._ykcat2 = None
        self._dll: Optional[ctypes.WinDLL] = None
        self._handle = ctypes.c_int(0)
        self._node = None
        self._loaded = False

    # ------------------------------------------------------------------ #
    # SDK lifecycle

    def load(self, *, ip: Optional[str] = None, port: int = 6000) -> None:
        """Load the YKCat2 SDK and optionally connect via TCP."""
        self._import_sdk()
        self._load_runtime()
        if ip:
            handle = ctypes.c_int()
            rc = self._ykcat2.YKM_SysConnect(
                self._dll, ip.encode("ascii"), int(port), handle
            )
            self._check_rc(rc, "YKM_SysConnect")
            self._handle = handle
        else:
            self._handle = ctypes.c_int(0)

        rc = self._ykcat2.YKM_SysLoadLib(self._dll, self._handle.value)
        self._check_rc(rc, "YKM_SysLoadLib")
        self._node = getattr(self._ykcat2.YKE_NODE, self._node_name)
        self._loaded = True

    def unload(self) -> None:
        """Release the SDK resources."""
        if not self._loaded:
            return
        rc = self._ykcat2.YKM_SysUnloadLib(self._dll, self._handle.value)
        self._check_rc(rc, "YKM_SysUnloadLib")
        self._loaded = False

    def __enter__(self) -> "ProConController":
        if not self._loaded:
            self.load()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.unload()

    # ------------------------------------------------------------------ #
    # System helpers

    @property
    def handle(self) -> int:
        return int(self._handle.value)

    @property
    def module(self):
        return self._ykcat2

    def wait_bus_ready(self, timeout: float = 10.0, poll_interval: float = 0.05) -> None:
        """Block until the EtherCAT bus reports RUNNING."""
        end_time = time.time() + timeout
        status = self._ykcat2.YKS_BusStatus()
        while True:
            rc = self._ykcat2.YKM_ReadBusStatus(
                self._dll, self.handle, self._node.value, status
            )
            self._check_rc(rc, "YKM_ReadBusStatus")
            if status.bus_status == self._ykcat2.YKE_BUS_STATUS.YKE_BUS_STATUS_RUNNING:
                return
            if time.time() >= end_time:
                raise ProConDllError("Timed out waiting for EtherCAT bus RUNNING state.")
            time.sleep(poll_interval)

    def warm_reset(self) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_SysWarmReset(self._dll, self.handle, self._node.value)
        self._check_rc(rc, "YKM_SysWarmReset")

    def clear_bus_warn(self) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_ClearBusWarn(self._dll, self.handle, self._node.value)
        self._check_rc(rc, "YKM_ClearBusWarn")

    def clear_system_warn(self) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_ClearSysWarn(self._dll, self.handle, self._node.value)
        self._check_rc(rc, "YKM_ClearSysWarn")

    def get_axis_list(self, max_axes: int = 32) -> list[int]:
        self._ensure_loaded()
        axis_num = ctypes.c_uint(0)
        axis_list = (ctypes.c_uint * max_axes)()
        rc = self._ykcat2.YKM_GetAxisList(
            self._dll, self.handle, axis_num, axis_list, ctypes.c_uint(max_axes)
        )
        self._check_rc(rc, "YKM_GetAxisList")
        return [int(axis_list[i]) for i in range(axis_num.value)]

    # ------------------------------------------------------------------ #
    # Axis operations

    def set_axis_soft_limit(
        self,
        axis_index: int,
        *,
        positive: float,
        negative: float,
        enable: bool = True,
    ) -> None:
        self._ensure_loaded()
        config = self._ykcat2.YKS_AxisSoftLimitConfig()
        config.positive = float(positive)
        config.negative = float(negative)
        config.enable = 1 if enable else 0
        rc = self._ykcat2.YKM_SetAxisSoftLimit(self._dll, self.handle, axis_index, config)
        self._check_rc(rc, "YKM_SetAxisSoftLimit")

    def set_command_equiv(
        self,
        axis_index: int,
        numerator: float,
        denominator: float,
    ) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_SetCommandEquiv(
            self._dll, self.handle, axis_index, numerator, denominator
        )
        self._check_rc(rc, "YKM_SetCommandEquiv")

    def set_axis_position(self, axis_index: int, position: float) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_SetAxisPosition(
            self._dll, self.handle, axis_index, float(position)
        )
        self._check_rc(rc, "YKM_SetAxisPosition")

    def power_on(self, axis_index: int) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_PowerOn(self._dll, self.handle, axis_index)
        self._check_rc(rc, "YKM_PowerOn")

    def power_off(self, axis_index: int) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_PowerOff(self._dll, self.handle, axis_index)
        self._check_rc(rc, "YKM_PowerOff")

    def read_axis_status(self, axis_index: int):
        self._ensure_loaded()
        status = self._ykcat2.YKS_AxisStatusBase()
        rc = self._ykcat2.YKM_ReadAxisStatusBase(
            self._dll, self.handle, axis_index, status
        )
        self._check_rc(rc, "YKM_ReadAxisStatusBase")
        return status

    def read_axis_position(self, axis_index: int) -> float:
        self._ensure_loaded()
        position = ctypes.c_double()
        rc = self._ykcat2.YKM_ReadAxisActualPosition(
            self._dll, self.handle, axis_index, position
        )
        self._check_rc(rc, "YKM_ReadAxisActualPosition")
        return float(position.value)

    def read_axis_command_position(self, axis_index: int) -> float:
        self._ensure_loaded()
        position = ctypes.c_double()
        rc = self._ykcat2.YKM_ReadAxisCommandPosition(
            self._dll, self.handle, axis_index, position
        )
        self._check_rc(rc, "YKM_ReadAxisCommandPosition")
        return float(position.value)

    def read_axis_velocity(self, axis_index: int) -> float:
        self._ensure_loaded()
        velocity = ctypes.c_double()
        rc = self._ykcat2.YKM_ReadAxisActualVelocity(
            self._dll, self.handle, axis_index, velocity
        )
        self._check_rc(rc, "YKM_ReadAxisActualVelocity")
        return float(velocity.value)

    def read_axis_torque(self, axis_index: int) -> float:
        self._ensure_loaded()
        torque = ctypes.c_double()
        rc = self._ykcat2.YKM_ReadAxisActualTorque(
            self._dll, self.handle, axis_index, torque
        )
        self._check_rc(rc, "YKM_ReadAxisActualTorque")
        return float(torque.value)

    def clear_axis_warn(self, axis_index: int) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_ClearAxisWarn(self._dll, self.handle, axis_index)
        self._check_rc(rc, "YKM_ClearAxisWarn")

    def clear_drive_warn(self, axis_index: int) -> None:
        self._ensure_loaded()
        rc = self._ykcat2.YKM_ClearDrvWarn(self._dll, self.handle, axis_index)
        self._check_rc(rc, "YKM_ClearDrvWarn")

    def clear_axis_error(self, axis_index: int) -> None:
        self.clear_axis_warn(axis_index)
        time.sleep(0.05)
        self.clear_drive_warn(axis_index)

    def wait_axis_idle(
        self,
        axis_index: int,
        *,
        timeout: float = 10.0,
        poll_interval: float = 0.02,
    ) -> None:
        end_time = time.time() + timeout
        while True:
            status = self.read_axis_status(axis_index)
            if status.active == 0:
                return
            if time.time() >= end_time:
                raise ProConDllError(f"Axis {axis_index} did not go idle in time.")
            time.sleep(poll_interval)

    def wait_axis_done(
        self,
        axis_index: int,
        *,
        timeout: float = 30.0,
        poll_interval: float = 0.02,
    ) -> None:
        end_time = time.time() + timeout
        while True:
            status = self.read_axis_status(axis_index)
            if bool(status.done):
                return
            if time.time() >= end_time:
                raise ProConDllError(f"Axis {axis_index} did not report done in time.")
            time.sleep(poll_interval)

    def move_absolute(
        self,
        axis_index: int,
        position: float,
        *,
        velocity: float,
        acceleration: float,
        deceleration: float,
        jerk_acc: Optional[float] = None,
        jerk_dec: Optional[float] = None,
        wait: bool = True,
        timeout: float = 30.0,
    ) -> None:
        config = self._ykcat2.YKS_MoveAbsoluteConfig()
        config.position = float(position)
        config.motion = self._create_motion_profile(
            velocity=velocity,
            acceleration=acceleration,
            deceleration=deceleration,
            jerk_acc=jerk_acc,
            jerk_dec=jerk_dec,
        )
        self._ensure_loaded()
        rc = self._ykcat2.YKM_MoveAbsoluteEx(self._dll, self.handle, axis_index, config)
        self._check_rc(rc, "YKM_MoveAbsoluteEx")
        if wait:
            self.wait_axis_done(axis_index, timeout=timeout)

    def move_relative(
        self,
        axis_index: int,
        distance: float,
        *,
        velocity: float,
        acceleration: float,
        deceleration: float,
        jerk_acc: Optional[float] = None,
        jerk_dec: Optional[float] = None,
        wait: bool = True,
        timeout: float = 30.0,
    ) -> None:
        config = self._ykcat2.YKS_MoveRelativeConfig()
        config.distance = float(distance)
        config.motion = self._create_motion_profile(
            velocity=velocity,
            acceleration=acceleration,
            deceleration=deceleration,
            jerk_acc=jerk_acc,
            jerk_dec=jerk_dec,
        )
        rc = self._ykcat2.YKM_MoveRelativeEx(self._dll, self.handle, axis_index, config)
        self._check_rc(rc, "YKM_MoveRelativeEx")
        if wait:
            self.wait_axis_done(axis_index, timeout=timeout)

    def move_velocity(
        self,
        axis_index: int,
        velocity: float,
    ) -> None:
        direction = (
            self._ykcat2.YKE_DIRECTION.YKE_DIRECTION_POSITIVE
            if velocity >= 0
            else self._ykcat2.YKE_DIRECTION.YKE_DIRECTION_NEGATIVE
        )
        rc = self._ykcat2.YKM_MoveVelocity(
            self._dll, self.handle, axis_index, float(velocity), direction.value
        )
        self._check_rc(rc, "YKM_MoveVelocity")

    def move_velocity_ex(
        self,
        axis_index: int,
        velocity: float,
        *,
        acceleration: float,
        deceleration: float,
        jerk_acc: Optional[float] = None,
        jerk_dec: Optional[float] = None,
    ) -> None:
        config = self._ykcat2.YKS_MoveVelocityConfig()
        config.direction = (
            self._ykcat2.YKE_DIRECTION.YKE_DIRECTION_POSITIVE
            if velocity >= 0
            else self._ykcat2.YKE_DIRECTION.YKE_DIRECTION_NEGATIVE
        ).value
        config.motion = self._create_motion_profile(
            velocity=abs(velocity),
            acceleration=acceleration,
            deceleration=deceleration,
            jerk_acc=jerk_acc,
            jerk_dec=jerk_dec,
        )
        rc = self._ykcat2.YKM_MoveVelocityEx(self._dll, self.handle, axis_index, config)
        self._check_rc(rc, "YKM_MoveVelocityEx")

    def stop_axis(self, axis_index: int, *, emergency: bool = False) -> None:
        mode = (
            self._ykcat2.YKE_STOP_DEC.YKE_STOP_SEL_EMG
            if emergency
            else self._ykcat2.YKE_STOP_DEC.YKE_STOP_SEL_SMOOTH
        )
        rc = self._ykcat2.YKM_StopAxis(self._dll, self.handle, axis_index, mode.value)
        self._check_rc(rc, "YKM_StopAxis")

    def start_home(
        self,
        axis_index: int,
        *,
        mode: int,
        velocity_high: float,
        velocity_low: float,
        acceleration: float,
        jerk: float,
        switch_move: float,
        probe_move: float,
        offset: float = 0.0,
    ) -> None:
        config = self._ykcat2.YKS_AxisHomeConfig()
        config.mode = self._enum_value(self._ykcat2.YKE_HOME_MODE, mode)
        config.curve_type = self._ykcat2.YKE_CURVE_TYPE.YKE_CURVE_S7.value
        config.vel_high = float(velocity_high)
        config.vel_low = float(velocity_low)
        config.acceleration = float(acceleration)
        config.jerk = float(jerk)
        config.switch_move = float(switch_move)
        config.probe_move = float(probe_move)
        config.offset = float(offset)
        rc = self._ykcat2.YKM_StartHome(self._dll, self.handle, axis_index, config)
        self._check_rc(rc, "YKM_StartHome")

    # ------------------------------------------------------------------ #
    # Group operations

    def init_group(
        self,
        group_id: int,
        axis_indices: Sequence[int],
        *,
        buffer_depth: int = 1024,
        cnc_enable: bool = False,
    ) -> None:
        if not axis_indices:
            raise ValueError("axis_indices must not be empty.")
        if len(axis_indices) > 32:
            raise ValueError("A group can contain at most 32 axes.")

        config = self._ykcat2.YKS_GroupConfig()
        config.buffer_depth = int(buffer_depth)
        config.axis_num = len(axis_indices)
        for idx, axis in enumerate(axis_indices):
            config.axis_list[idx] = int(axis)
        config.cnc_enable = 1 if cnc_enable else 0

        rc = self._ykcat2.YKM_InitGroup(self._dll, self.handle, group_id, config)
        self._check_rc(rc, "YKM_InitGroup")

    def set_group_profile(
        self,
        group_id: int,
        *,
        max_velocity: float,
        stop_dec_emg: float,
        stop_dec_smooth: float,
        stop_dec_jerk: float,
    ) -> None:
        profile = self._ykcat2.YKS_GroupProfile()
        profile.max_velocity = float(max_velocity)
        profile.stop_dec_emg = float(stop_dec_emg)
        profile.stop_dec_smooth = float(stop_dec_smooth)
        profile.stop_dec_jerk = float(stop_dec_jerk)
        rc = self._ykcat2.YKM_SetGroupProfile(self._dll, self.handle, group_id, profile)
        self._check_rc(rc, "YKM_SetGroupProfile")

    def move_linear_absolute(
        self,
        group_id: int,
        axis_indices: Sequence[int],
        positions: Sequence[float],
        *,
        velocity: float,
        acceleration: float,
        deceleration: float,
        jerk: float,
        buffer_mode: int = 0,
        trans_mode: int = 0,
    ) -> None:
        if len(axis_indices) != len(positions):
            raise ValueError("axis_indices and positions length mismatch.")
        config = self._ykcat2.YKS_MoveLinearAbsoluteConfig()
        config.axis_num = len(axis_indices)
        for idx, axis in enumerate(axis_indices):
            config.axis_list[idx] = int(axis)
            config.position[idx] = float(positions[idx])
        config.velocity = float(velocity)
        config.acceleration = float(acceleration)
        config.deceleration = float(deceleration)
        config.jerk = float(jerk)
        config.buffer_mode = int(buffer_mode)
        config.trans_mode = int(trans_mode)
        rc = self._ykcat2.YKM_MoveLinearAbsolute(self._dll, self.handle, group_id, config)
        self._check_rc(rc, "YKM_MoveLinearAbsolute")

    def start_group(self, group_id: int) -> None:
        rc = self._ykcat2.YKM_StartGroup(self._dll, self.handle, group_id)
        self._check_rc(rc, "YKM_StartGroup")

    def stop_group(self, group_id: int, *, emergency: bool = False) -> None:
        mode = (
            self._ykcat2.YKE_STOP_DEC.YKE_STOP_SEL_EMG
            if emergency
            else self._ykcat2.YKE_STOP_DEC.YKE_STOP_SEL_SMOOTH
        )
        rc = self._ykcat2.YKM_StopGroup(self._dll, self.handle, group_id, mode.value)
        self._check_rc(rc, "YKM_StopGroup")

    def read_group_status(self, group_id: int):
        status = self._ykcat2.YKS_GroupStatusBase()
        rc = self._ykcat2.YKM_ReadGroupStatusBase(
            self._dll, self.handle, group_id, status
        )
        self._check_rc(rc, "YKM_ReadGroupStatusBase")
        return status

    def clear_group_warn(self, group_id: int) -> None:
        rc = self._ykcat2.YKM_ClearGroupWarn(self._dll, self.handle, group_id)
        self._check_rc(rc, "YKM_ClearGroupWarn")

    def deinit_group(self, group_id: int) -> None:
        rc = self._ykcat2.YKM_DeInitGroup(self._dll, self.handle, group_id)
        self._check_rc(rc, "YKM_DeInitGroup")

    def follow_ug(self, axis_index: int, config) -> None:
        """Execute a FollowUG command with a prepared configuration."""
        rc = self._ykcat2.YKM_FollowUG(self._dll, self.handle, axis_index, config)
        self._check_rc(rc, "YKM_FollowUG")

    # ------------------------------------------------------------------ #
    # Digital IO

    def write_digital_output(self, point: DigitalPoint, state: bool) -> None:
        value = (
            self._ykcat2.YKE_BOOL.YKE_TRUE.value
            if state
            else self._ykcat2.YKE_BOOL.YKE_FALSE.value
        )
        rc = self._ykcat2.YKM_WriteDigitalOutputBit(
            self._dll, self.handle, point.slave_id, point.index, value
        )
        self._check_rc(rc, "YKM_WriteDigitalOutputBit")

    def read_digital_output(self, point: DigitalPoint) -> bool:
        value = ctypes.c_uint32()
        rc = self._ykcat2.YKM_ReadDigitalOutputBit(
            self._dll, self.handle, point.slave_id, point.index, value
        )
        self._check_rc(rc, "YKM_ReadDigitalOutputBit")
        return bool(value.value)

    def read_digital_input(self, point: DigitalPoint) -> bool:
        value = ctypes.c_uint32()
        rc = self._ykcat2.YKM_ReadDigitalInputBit(
            self._dll, self.handle, point.slave_id, point.index, value
        )
        self._check_rc(rc, "YKM_ReadDigitalInputBit")
        return bool(value.value)

    def wait_digital_input(
        self,
        point: DigitalPoint,
        state: bool,
        *,
        timeout: float = 5.0,
        poll_interval: float = 0.01,
    ) -> None:
        end_time = time.time() + timeout
        while True:
            current = self.read_digital_input(point)
            if current == state:
                return
            if time.time() >= end_time:
                raise ProConDllError(
                    f"Digital input {point.slave_id}:{point.index} did not reach state {int(state)}."
                )
            time.sleep(poll_interval)

    def operate_cylinder(
        self,
        output: DigitalPoint,
        *,
        extend: bool,
        feedback: Optional[DigitalPoint] = None,
        timeout: float = 5.0,
        poll_interval: float = 0.02,
    ) -> None:
        self.write_digital_output(output, extend)
        if feedback:
            self.wait_digital_input(
                feedback, state=extend, timeout=timeout, poll_interval=poll_interval
            )

    def write_pdo_object(
        self,
        node: int,
        slave_index: int,
        main_index: int,
        sub_index: int,
        value: int,
        size: int = 1,
    ) -> None:
        rc = self._ykcat2.YKM_WritePDOObject(
            self._dll,
            self.handle,
            node,
            slave_index,
            main_index,
            sub_index,
            value,
            size,
        )
        self._check_rc(rc, "YKM_WritePDOObject")

    def read_pdo_object(
        self,
        node: int,
        slave_index: int,
        main_index: int,
        sub_index: int,
        *,
        size: int = 4,
        signed: bool = False,
    ) -> int:
        buffer = (ctypes.c_ubyte * size)()
        rc = self._ykcat2.YKM_ReadPDOObject(
            self._dll,
            self.handle,
            node,
            slave_index,
            main_index,
            sub_index,
            buffer,
            size,
        )
        self._check_rc(rc, "YKM_ReadPDOObject")
        raw = bytes(buffer)
        return int.from_bytes(raw, byteorder="little", signed=signed)

    # ------------------------------------------------------------------ #
    # Internal helpers

    def _import_sdk(self) -> None:
        if self._ykcat2:
            return
        if not self._include_dir.exists():
            raise ProConDllError(f"Include directory not found: {self._include_dir}")
        if str(self._include_dir) not in sys.path:
            sys.path.insert(0, str(self._include_dir))
        self._ykcat2 = importlib.import_module("YKCat2")

    def _load_runtime(self) -> None:
        if self._dll:
            return
        if not self._dll_dir.exists():
            raise ProConDllError(f"DLL directory not found: {self._dll_dir}")
        dll_path = self._dll_dir / "YKCat2.dll"
        if not dll_path.exists():
            raise ProConDllError(f"Missing YKCat2.dll in {self._dll_dir}")
        self._dll = ctypes.WinDLL(str(dll_path))
        nosys_path = self._dll_dir / "NoSys.dll"
        if nosys_path.exists():
            ctypes.WinDLL(str(nosys_path))

    def _create_motion_profile(
        self,
        *,
        velocity: float,
        acceleration: float,
        deceleration: float,
        jerk_acc: Optional[float],
        jerk_dec: Optional[float],
        start_velocity: float = 0.0,
        stop_velocity: float = 0.0,
        constant_velocity_time: float = 0.0,
        constant_acc_time: float = 0.0,
        constant_dec_time: float = 0.0,
    ):
        profile = self._ykcat2.YKS_AxisProfileMotion()
        profile.curve_type = self._ykcat2.YKE_CURVE_TYPE.YKE_CURVE_S7.value
        profile.start_velocity = float(start_velocity)
        profile.stop_velocity = float(stop_velocity)
        profile.velocity = float(velocity)
        profile.acceleration = float(acceleration)
        profile.deceleration = float(deceleration)
        profile.jerk_acc = float(jerk_acc if jerk_acc is not None else acceleration * 10.0)
        profile.jerk_dec = float(jerk_dec if jerk_dec is not None else deceleration * 10.0)
        profile.constant_velocity_time = float(constant_velocity_time)
        profile.constant_acc_time = float(constant_acc_time)
        profile.constant_dec_time = float(constant_dec_time)
        profile.smooth_time = 0.0
        return profile

    def _enum_value(self, enum_cls, value, default=None) -> int:
        if value is None:
            value = default
        if isinstance(value, Enum):
            return int(value.value)
        if value is None:
            raise ValueError("Enum value cannot be None.")
        try:
            return int(enum_cls(value).value)  # type: ignore[arg-type]
        except Exception:
            return int(value)

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise ProConDllError("SDK is not loaded. Call load() first.")

    def _check_rc(self, rc: int, context: str) -> None:
        if rc == self._ykcat2.YKE_RESULT_CODE.YKE_RET_OK.value:
            return
        try:
            code = self._ykcat2.YKE_RESULT_CODE(rc)
            message = f"{code.name}({int(rc)})"
        except ValueError:
            message = str(int(rc))
        raise ProConDllError(f"{context} failed: {message}")
