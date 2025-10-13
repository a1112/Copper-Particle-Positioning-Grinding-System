from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QCoreApplication

from app.core.events import EventBus
from app.process.orchestrator import Orchestrator
from app.devices.sim.motion_sim import MotionSim
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim

from app.ui.image_provider import CameraImageProvider
from app.ui.qml_bridge import Backend
from app.ui.settings_bridge import SettingsBridge
from app.ui.highlighter import HighlighterBridge
from api.server import create_app
from app.server.launcher import ApiController


class Runtime:
    def __init__(self) -> None:
        # Core domain
        self.bus = EventBus()
        self.motion = MotionSim()
        self.orch = Orchestrator(self.bus, self.motion)

        # Vision/camera
        self.vision = VisionPipeline(self.bus)
        self.camera = CameraSim()

        # UI provider/context
        self.provider = CameraImageProvider()
        self.settings = SettingsBridge(Path(__file__).resolve().parents[1].joinpath('ui', 'config.json'))
        self.backend = Backend(self.orch)
        self.highlighter = HighlighterBridge()

        # Hook orchestrator to UI backend for vision target
        try:
            self.orch.backend = self.backend  # type: ignore[attr-defined]
        except Exception:
            pass

        # API
        self.api_app = create_app(self.provider, self.orch, self.motion)
        self.api_ctl = ApiController()

        # Qt objects
        self.app: Optional[QGuiApplication] = None
        self.engine: Optional[QQmlApplicationEngine] = None

    # --- Vision / Camera wiring ---
    def start_camera(self) -> None:
        self.camera.open()

        def on_frame(frame):
            self.vision.on_frame(frame)
            try:
                self.provider.set_frame(frame)
            except Exception:
                pass

        self.camera.start_stream(on_frame)

    def stop_camera(self) -> None:
        try:
            self.camera.stop_stream()
            self.camera.close()
        except Exception:
            pass

    # --- API control ---
    def start_api(self) -> None:
        self.api_ctl.start(self.api_app, self.settings.apiPort)

    def restart_api(self, port: int) -> None:
        self.api_ctl.restart(self.api_app, port)

    # --- Qt / QML bootstrapping ---
    def create_qml(self) -> None:
        self.app = QGuiApplication([])
        QCoreApplication.setOrganizationName("CopperSystem")
        QCoreApplication.setOrganizationDomain("example.local")
        QCoreApplication.setApplicationName("Copper UI")

        self.engine = QQmlApplicationEngine()
        self.engine.addImageProvider('camera', self.provider)
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty("pyHighlighter", self.highlighter)
        self.engine.rootContext().setContextProperty("settings", self.settings)

        # Bind API restart hook
        def _api_hook(action: str, port: int):
            if action == "restart":
                self.restart_api(port)

        try:
            self.settings.bindController(_api_hook)
        except Exception:
            pass

    def load_main_qml(self, qml_path: Optional[Path] = None) -> None:
        assert self.engine is not None
        if qml_path is None:
            qml_path = Path(__file__).resolve().parents[1].joinpath('ui', 'qml', 'main.qml')
        self.engine.load(str(qml_path))

    def exec(self) -> int:
        assert self.app is not None
        return self.app.exec()

