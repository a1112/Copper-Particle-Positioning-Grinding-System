import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from pathlib import Path

from app.core.events import EventBus
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim
from app.devices.sim.motion_sim import MotionSim
from app.process.orchestrator import Orchestrator
from app.ui.qml_bridge import Backend
from app.ui.image_provider import CameraImageProvider
from app.ui.settings_bridge import SettingsBridge
from app.ui.highlighter import HighlighterBridge
from app.api.server import create_app
from app.api.launcher import ApiController


def main():
    bus = EventBus()
    motion = MotionSim()
    orch = Orchestrator(bus, motion)

    # Vision wiring
    vision = VisionPipeline(bus)
    cam = CameraSim()
    cam.open()
    # Bridge frames into image provider
    def on_frame(frame):
        vision.on_frame(frame)
        try:
            provider.set_frame(frame)
        except Exception:
            pass

    cam.start_stream(on_frame)

    app = QGuiApplication(sys.argv)
    from PySide6.QtCore import QCoreApplication
    QCoreApplication.setOrganizationName("CopperSystem")
    QCoreApplication.setOrganizationDomain("example.local")
    QCoreApplication.setApplicationName("Copper UI")
    engine = QQmlApplicationEngine()
    provider = CameraImageProvider()
    engine.addImageProvider('camera', provider)
    settings = SettingsBridge(Path(__file__).resolve().parent.joinpath('ui', 'config.json'))
    engine.rootContext().setContextProperty("settings", settings)
    engine.rootContext().setContextProperty("pyHighlighter", HighlighterBridge())

    backend = Backend(orch)
    # let orchestrator notify backend for vision results
    try:
        orch.backend = backend
    except Exception:
        pass
    engine.rootContext().setContextProperty("backend", backend)
    engine.load("app/ui/qml/main.qml")
    if not engine.rootObjects():
        sys.exit(-1)

    # Launch FastAPI via controllable controller
    app_api = create_app(provider, orch, motion)
    api_ctl = ApiController()
    api_ctl.start(app_api, settings.apiPort)
    # Bind restart hook into settings bridge
    def _api_hook(action: str, port: int):
        if action == "restart":
            api_ctl.restart(app_api, port)
    try:
        settings.bindController(_api_hook)
    except Exception:
        pass

    ret = app.exec()
    cam.stop_stream()
    cam.close()
    sys.exit(ret)

if __name__ == '__main__':
    main()
