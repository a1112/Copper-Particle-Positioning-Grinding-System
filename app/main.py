from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from app.config import DATA_MODE, DATA_ENDPOINT
from app.runtime.environment import bootstrap_environment
from app.ui.src.highlighter import HighlighterBridge
from app.ui.src.localization import LocalizationManager, read_persisted_language
from app.server.launcher import ApiController


def main() -> None:
    """Application entry point."""
    bindings, _service = bootstrap_environment(DATA_MODE, endpoint=DATA_ENDPOINT)
    motion = bindings.motion
    orch = bindings.orchestrator
    vision = bindings.vision
    cam = bindings.camera
    cam.open()

    app = QGuiApplication(sys.argv)
    from PySide6.QtCore import QCoreApplication, QUrl, QSettings
    from app.ui.main import _ensure_qrc_resources

    QCoreApplication.setOrganizationName("CopperSystem")
    QCoreApplication.setOrganizationDomain("example.local")
    QCoreApplication.setApplicationName("Copper UI")
    try:
        _ensure_qrc_resources()
        app.setWindowIcon(QIcon(":/resource/app.ico"))
    except Exception:
        pass

    translations_dir = Path(__file__).resolve().parent.joinpath("ui", "i18n")
    initial_language = read_persisted_language()
    i18n = LocalizationManager(translations_dir, initial_language)

    engine = QQmlApplicationEngine()

    def on_frame(frame):
        try:
            vision.on_frame(frame)
        except Exception:
            pass

    cam.start_stream(on_frame)

    engine.rootContext().setContextProperty("pyHighlighter", HighlighterBridge())
    engine.rootContext().setContextProperty("i18n", i18n)

    qml_path = Path(__file__).resolve().parent.joinpath("ui", "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        cam.stop_stream()
        cam.close()
        sys.exit(-1)

    api_ctl = ApiController()

    settings_store = QSettings()
    port_value = settings_store.value("apiPort", 8010)
    try:
        api_port = int(port_value)
    except Exception:
        api_port = 8010


    ret = app.exec()
    cam.stop_stream()
    cam.close()
    sys.exit(ret)


if __name__ == "__main__":
    main()
