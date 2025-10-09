import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from app.core.events import EventBus
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim
from app.devices.sim.motion_sim import MotionSim
from app.process.orchestrator import Orchestrator
from app.ui.qml_bridge import Backend
from app.ui.image_provider import CameraImageProvider
from app.ui.highlighter import HighlighterBridge
from app.api.server import create_app


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
    engine = QQmlApplicationEngine()
    provider = CameraImageProvider()
    engine.addImageProvider('camera', provider)
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

    # launch FastAPI in background thread
    try:
        import threading
        import uvicorn
        import os
        app_api = create_app(provider, orch, motion)
        def run_api():
            port = int(os.getenv("COPPER_API_PORT", "8010"))
            uvicorn.run(app_api, host="127.0.0.1", port=port, log_level="warning")
        t = threading.Thread(target=run_api, daemon=True)
        t.start()
    except Exception as e:
        print(e)

    ret = app.exec()
    cam.stop_stream()
    cam.close()
    sys.exit(ret)

if __name__ == '__main__':
    main()
