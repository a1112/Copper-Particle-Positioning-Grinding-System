from __future__ import annotations

import sys
from pathlib import Path



def _ensure_project_root_on_path() -> None:
    # Add project root to sys.path so `import app.*` works when running this file directly
    here = Path(__file__).resolve()
    project_root = here.parents[2]  # .../Copper-Particle-Positioning-Grinding-System
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def _run_full_app() -> int:
    """Delegate to the main application entrypoint if available."""
    from app.main import main as app_main  # type: ignore
    app_main()
    return 0


def _run_minimal_ui() -> int:
    """Fallback minimal UI launcher if full app stack isn't available."""
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from app.ui.qml_bridge import Backend
    from app.ui.image_provider import CameraImageProvider
    from app.ui.settings_bridge import SettingsBridge
    from app.ui.highlighter import HighlighterBridge

    class _DummyMotion:
        def home(self) -> None:
            pass

        def status(self):
            return (0.0, 0.0, 0.0, 0.0)

        def set_speed(self, v_fast: float, v_work: float) -> None:
            pass

        def jog(self, axis: str, direction: int, speed: float) -> None:
            pass

        def set_work_origin(self) -> None:
            pass

    class _DummyOrchestrator:
        def __init__(self) -> None:
            self.motion = _DummyMotion()

    app = QGuiApplication(sys.argv)
    from PySide6.QtCore import QCoreApplication
    QCoreApplication.setOrganizationName("CopperSystem")
    QCoreApplication.setOrganizationDomain("example.local")
    QCoreApplication.setApplicationName("Copper UI")
    engine = QQmlApplicationEngine()
    provider = CameraImageProvider()
    engine.addImageProvider('camera', provider)
    settings = SettingsBridge(Path(__file__).resolve().parent.joinpath('config.json'))
    engine.rootContext().setContextProperty("settings", settings)
    backend = Backend(_DummyOrchestrator())
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("pyHighlighter", HighlighterBridge())
    # Load QML from ./qml/main.qml to avoid cwd assumptions
    qml_path = str(Path(__file__).resolve().parent.joinpath("qml", "main.qml"))
    engine.load(qml_path)
    if not engine.rootObjects():
        return -1
    return app.exec()


def main() -> None:
    _ensure_project_root_on_path()
    try:
        sys.exit(_run_full_app())
    except Exception:
        # Fall back to a minimal, offline UI launcher
        ret = _run_minimal_ui()
        sys.exit(ret)


if __name__ == "__main__":
    main()
