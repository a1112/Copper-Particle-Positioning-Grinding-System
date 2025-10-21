from __future__ import annotations

import sys
from pathlib import Path
import shutil
import subprocess
import traceback


def _ensure_project_root_on_path() -> None:
    """Ensure the project root is on sys.path when running from app/ui."""
    here = Path(__file__).resolve()
    project_root = here.parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def _run_full_app() -> int:
    """Launch the full simulator + API + UI stack."""
    from app.main import main as app_main  # type: ignore

    app_main()
    return 0


def _ensure_qrc_resources() -> None:
    """Compile or register QML resources so the UI can load from .qrc files."""
    from PySide6.QtCore import QResource

    here = Path(__file__).resolve().parent
    qrc_list = [here / "qml.qrc", here / "resource.qrc"]
    rcc = shutil.which("rcc") or shutil.which("rcc.exe")
    pyside_rcc = (
        shutil.which("pyside6-rcc")
        or shutil.which("pyrcc5")
        or shutil.which("pyside2-rcc")
    )

    for qrc in qrc_list:
        if not qrc.exists():
            continue
        out_rcc = here / f"{qrc.stem}.rcc"
        if rcc:
            try:
                needs_compile = not out_rcc.exists() or out_rcc.stat().st_mtime < qrc.stat().st_mtime
                if needs_compile:
                    subprocess.run([rcc, "-binary", str(qrc), "-o", str(out_rcc)], check=True)
            except Exception:
                out_rcc = None
        if out_rcc and out_rcc.exists():
            QResource.registerResource(str(out_rcc))
            continue
        py_mod = here / f"{qrc.stem}_rc.py"
        if pyside_rcc:
            try:
                needs_py = not py_mod.exists() or py_mod.stat().st_mtime < qrc.stat().st_mtime
                if needs_py:
                    subprocess.run([pyside_rcc, str(qrc), "-o", str(py_mod)], check=True)
            except Exception:
                pass
        if py_mod.exists():
            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location(py_mod.stem, str(py_mod))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # type: ignore[attr-defined]
            except Exception:
                pass


def _run_minimal_ui() -> int:
    """Run a lightweight UI without Python backend bindings."""
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtCore import QCoreApplication, QUrl
    from app.ui.src.image_provider import CameraImageProvider
    from app.ui.src.highlighter import HighlighterBridge
    from app.ui.src.localization import LocalizationManager, read_persisted_language

    app = QGuiApplication(sys.argv)
    QCoreApplication.setOrganizationName("CopperSystem")
    QCoreApplication.setOrganizationDomain("example.local")
    QCoreApplication.setApplicationName("Copper UI")

    engine = QQmlApplicationEngine()
    try:
        _ensure_qrc_resources()
    except Exception:
        try:
            sys.stderr.write("[warn] qrc auto-compile/register failed\n")
            sys.stderr.write(traceback.format_exc() + "\n")
        except Exception:
            pass

    provider = CameraImageProvider()
    engine.addImageProvider("camera", provider)

    translations_dir = Path(__file__).resolve().parent.joinpath("i18n")
    initial_language = read_persisted_language()
    i18n = LocalizationManager(translations_dir, initial_language)
    engine.rootContext().setContextProperty("pyHighlighter", HighlighterBridge())
    engine.rootContext().setContextProperty("i18n", i18n)

    qml_path = Path(__file__).resolve().parent.joinpath("qml", "main.qml")
    try:
        try:
            sys.stderr.write(f"Loading QML: {qml_path}\n")
        except Exception:
            pass
        engine.load(QUrl.fromLocalFile(str(qml_path)))
    except Exception as exc:
        sys.stderr.write(f"QML load exception: {exc}\n")
        return -1

    if not engine.rootObjects():
        try:
            for warning in engine.warnings():
                sys.stderr.write(str(warning.toString()) + "\n")
        except Exception:
            pass
        return -1

    return app.exec()


def main() -> None:
    """Entry point that prefers the minimal UI when run from app/ui."""
    _ensure_project_root_on_path()
    args = {arg.lower() for arg in sys.argv[1:]}
    here = Path(__file__).resolve().parent
    force_minimal = any(flag in args for flag in {"--minimal", "--ui-only", "-m"})
    if Path.cwd().resolve() == here and not force_minimal:
        force_minimal = True

    if force_minimal:
        ret = _run_minimal_ui()
        sys.exit(ret)

    try:
        sys.exit(_run_full_app())
    except BaseException:
        ret = _run_minimal_ui()
        sys.exit(ret)


if __name__ == "__main__":
    main()