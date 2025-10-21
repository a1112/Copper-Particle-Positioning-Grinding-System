from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QCoreApplication, QSettings

from app.api.server import create_app
from app.config import DATA_MODE, DATA_ENDPOINT
from app.runtime.environment import bootstrap_environment
from app.ui.src.highlighter import HighlighterBridge
from app.ui.src.image_provider import CameraImageProvider
from app.ui.src.localization import LocalizationManager, read_persisted_language
from app.server.launcher import ApiController


class Runtime:
    def __init__(self) -> None:
        bindings, self.business_service = bootstrap_environment(DATA_MODE, endpoint=DATA_ENDPOINT)

        # Core domain
        self.bus = bindings.bus
        self.motion = bindings.motion
        self.orch = bindings.orchestrator

        # Vision/camera
        self.vision = bindings.vision
        self.camera = bindings.camera

        # UI provider/context
        self.provider = CameraImageProvider()
        self.highlighter = HighlighterBridge()
        self.i18n: Optional[LocalizationManager] = None

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
        self.api_ctl.start(self.api_app, self._resolve_api_port())

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

        translations_dir = Path(__file__).resolve().parents[1].joinpath('ui', 'i18n')
        initial_language = read_persisted_language()
        self.i18n = LocalizationManager(translations_dir, initial_language)

        self.engine.rootContext().setContextProperty("pyHighlighter", self.highlighter)
        self.engine.rootContext().setContextProperty("i18n", self.i18n)

    def load_main_qml(self, qml_path: Optional[Path] = None) -> None:
        assert self.engine is not None
        from PySide6.QtCore import QUrl
        if qml_path is None:
            qml_path = Path(__file__).resolve().parents[1].joinpath('ui', 'qml', 'main.qml')
        self.engine.load(QUrl.fromLocalFile(str(qml_path)))

    def exec(self) -> int:
        assert self.app is not None
        return self.app.exec()

    def _resolve_api_port(self) -> int:
        settings = QSettings("CopperSystem", "Copper UI")
        value = settings.value("apiPort", 8010)
        try:
            return int(value)
        except Exception:
            return 8010

