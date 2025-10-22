from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from importlib import import_module
from typing import Optional, Tuple, Type, TypeVar, Any

from app.config import RPC_CONTROL_ENDPOINT, RPC_LISTEN_ENDPOINT, RPC_TIMEOUT
from app.core.events import EventBus
from app.devices.camera_base import ICamera
from app.devices.motion_base import IMotionController
from app.devices.sim.camera_sim import CameraSim
from app.devices.sim.motion_sim import MotionSim
from app.devices.sim.virtual_parameter_device import VirtualParameterDevice
from app.domain.status import set_status_provider
from app.domain.status.providers import SimStatusProvider, ProductionStatusProvider
from app.process.orchestrator import Orchestrator
from app.process.sim_executor import SimulatedProcessExecutor
from app.process.sim_path_planner import SimulatedPathPlanner
from app.server.business import BusinessService, RuntimeBusinessService, SimBusinessService, RpcBusinessService
from app.server.data import set_backend
from app.server.rpc import RpcControlClient, RpcDataStore, RpcServerRunner, RpcStatusProvider
from app.vision.pipeline import VisionPipeline

_LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


def _load_optional(target: str) -> Optional[Any]:
    """Import an optional plugin class from a dotted path 'module:attr'."""
    if not target:
        return None
    if ":" not in target:
        module_name, attr_name = target, None
    else:
        module_name, attr_name = target.split(":", 1)
    try:
        module = import_module(module_name)
    except ImportError as exc:  # pragma: no cover - optional dependency path
        _LOGGER.warning("Optional plugin %s not available: %s", target, exc)
        return None
    if attr_name:
        try:
            return getattr(module, attr_name)
        except AttributeError as exc:  # pragma: no cover - optional dependency path
            _LOGGER.warning("Plugin attribute %s missing in %s: %s", attr_name, module_name, exc)
            return None
    return module


@dataclass
class SystemBindings:
    """Aggregated objects required by the UI/API runtime."""

    bus: EventBus
    motion: IMotionController
    camera: ICamera
    orchestrator: Orchestrator
    vision: VisionPipeline
    parameter_device: Optional[VirtualParameterDevice] = None
    path_planner: Optional[SimulatedPathPlanner] = None
    process_engine: Optional[SimulatedProcessExecutor] = None

    @property
    def mode(self) -> str:
        return getattr(self.orchestrator, "_mode", "sim")


class BaseEnvironment(ABC):
    """Abstract provider that wires devices/business objects for a given mode."""

    mode: str = "base"

    def build(self) -> SystemBindings:
        bus = EventBus()
        motion = self.create_motion(bus)
        orchestrator = self.create_orchestrator(bus, motion)
        vision = self.create_vision(bus)
        camera = self.create_camera()
        setattr(orchestrator, "_mode", self.mode)
        return SystemBindings(bus=bus, motion=motion, camera=camera, orchestrator=orchestrator, vision=vision)

    def create_orchestrator(self, bus: EventBus, motion: IMotionController) -> Orchestrator:
        return Orchestrator(bus, motion)

    def create_vision(self, bus: EventBus) -> VisionPipeline:
        return VisionPipeline(bus)

    @abstractmethod
    def create_motion(self, bus: EventBus) -> IMotionController:
        ...

    @abstractmethod
    def create_camera(self) -> ICamera:
        ...

    @abstractmethod
    def configure_backend(self, bindings: SystemBindings, *, endpoint: Optional[str] = None) -> BusinessService:
        ...


class SimEnvironment(BaseEnvironment):
    """Simulation environment binding simulator devices and services."""

    mode = "sim"

    def __init__(self) -> None:
        super().__init__()
        self._status_provider = SimStatusProvider()
        self._parameter_device: Optional[VirtualParameterDevice] = None
        self._planner: Optional[SimulatedPathPlanner] = None
        self._executor: Optional[SimulatedProcessExecutor] = None

    def create_motion(self, bus: EventBus) -> IMotionController:  # noqa: ARG002
        return MotionSim()

    def create_camera(self) -> ICamera:
        return CameraSim()

    def build(self) -> SystemBindings:
        bindings = super().build()
        parameter_device = VirtualParameterDevice(self._status_provider)
        planner = SimulatedPathPlanner()
        executor = SimulatedProcessExecutor(bindings.motion, planner, parameter_device)
        executor.plan_and_record()
        setattr(bindings.orchestrator, "sim_executor", executor)
        setattr(bindings.orchestrator, "sim_planner", planner)
        setattr(bindings.orchestrator, "sim_device", parameter_device)
        self._parameter_device = parameter_device
        self._planner = planner
        self._executor = executor

        return SystemBindings(
            bus=bindings.bus,
            motion=bindings.motion,
            camera=bindings.camera,
            orchestrator=bindings.orchestrator,
            vision=bindings.vision,
            parameter_device=parameter_device,
            path_planner=planner,
            process_engine=executor,
        )

    def configure_backend(self, bindings: SystemBindings, *, endpoint: Optional[str] = None) -> BusinessService:  # noqa: ARG002
        service = SimBusinessService()
        set_status_provider(self._status_provider)
        set_backend(service)
        return service


class RuntimeEnvironment(BaseEnvironment):
    """Runtime/production environment. Falls back to simulator when plugins are missing."""

    mode = "runtime"

    def __init__(
        self,
        *,
        motion_plugin: Optional[str] = None,
        camera_plugin: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._motion_plugin = motion_plugin or "app.devices.plugins.motion_runtime:RuntimeMotion"
        self._camera_plugin = camera_plugin or "app.devices.plugins.camera_runtime:RuntimeCamera"

    def _instantiate_optional(self, target: str, fallback_cls: Type[T]) -> T:
        obj = _load_optional(target)
        if obj is None:
            _LOGGER.warning("Using simulator fallback for %s", target)
            return fallback_cls()
        if isinstance(obj, type):
            return obj()  # type: ignore[return-value]
        return obj  # type: ignore[return-value]

    def create_motion(self, bus: EventBus) -> IMotionController:  # noqa: ARG002
        return self._instantiate_optional(self._motion_plugin, MotionSim)

    def create_camera(self) -> ICamera:
        return self._instantiate_optional(self._camera_plugin, CameraSim)

    def configure_backend(self, bindings: SystemBindings, *, endpoint: Optional[str] = None) -> BusinessService:
        if endpoint:
            set_status_provider(ProductionStatusProvider(endpoint))
        else:
            _LOGGER.warning("Production endpoint not configured; using simulator status provider.")
            set_status_provider(SimStatusProvider())
        service = RuntimeBusinessService(bindings.motion, bindings.orchestrator)
        set_backend(service)
        return service


class RpcEnvironment(BaseEnvironment):
    """Environment that bridges the API to an external controller via ZeroRPC."""

    mode = "rpc"

    def __init__(
        self,
        *,
        listen_endpoint: Optional[str] = None,
        control_endpoint: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        super().__init__()
        self._listen_endpoint = listen_endpoint or RPC_LISTEN_ENDPOINT
        self._control_endpoint = control_endpoint or RPC_CONTROL_ENDPOINT
        self._timeout = RPC_TIMEOUT if timeout is None else timeout
        self._store = RpcDataStore()
        self._server_runner = RpcServerRunner(endpoint=self._listen_endpoint, store=self._store)
        self._control_client = RpcControlClient(endpoint=self._control_endpoint, timeout=self._timeout)

    def create_motion(self, bus: EventBus) -> IMotionController:  # noqa: ARG002
        return MotionSim()

    def create_camera(self) -> ICamera:
        return CameraSim()

    def configure_backend(self, bindings: SystemBindings, *, endpoint: Optional[str] = None) -> BusinessService:  # noqa: ARG002
        set_status_provider(RpcStatusProvider(self._store))
        service = RpcBusinessService(self._store, self._control_client)
        set_backend(service)
        try:
            self._server_runner.start()
            _LOGGER.info(
                "RPC bridge enabled (listen=%s, upstream=%s, timeout=%ss)",
                self._listen_endpoint,
                self._control_endpoint,
                self._timeout,
            )
        except Exception as exc:
            _LOGGER.error("Failed to start ZeroRPC server at %s: %s", self._listen_endpoint, exc)
            raise
        setattr(bindings.orchestrator, "rpc_store", self._store)
        setattr(bindings.orchestrator, "rpc_runner", self._server_runner)
        return service


def get_environment(mode: Optional[str] = None) -> BaseEnvironment:
    normalized = (mode or "sim").lower()
    if normalized in {"runtime", "production", "prod", "comm"}:
        return RuntimeEnvironment()
    if normalized in {"rpc", "zerorpc"}:
        return RpcEnvironment()
    return SimEnvironment()


def bootstrap_environment(mode: Optional[str] = None, *, endpoint: Optional[str] = None) -> Tuple[SystemBindings, BusinessService]:
    """Create system bindings and configure backend/status providers for the selected mode."""
    env = get_environment(mode)
    bindings = env.build()
    service = env.configure_backend(bindings, endpoint=endpoint)
    return bindings, service

