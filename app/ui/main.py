from __future__ import annotations

import sys
from pathlib import Path
import shutil
import subprocess
import traceback


def _ensure_project_root_on_path() -> None:
    """将项目根目录加入 sys.path（中文注释）

    作用：确保从 app/ui 目录直接运行时，`import app.*` 能够成功。
    """
    # 将项目根目录加入 sys.path，便于相对模块导入
    here = Path(__file__).resolve()
    project_root = here.parents[2]  # .../Copper-Particle-Positioning-Grinding-System
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def _run_full_app() -> int:
    """运行完整应用（中文注释）

    通过导入并调用 app.main.main 启动包含设备仿真、API 与 UI 的完整应用。
    返回：进程退出码（此处固定 0，真实退出码由上层控制）。
    """
    from app.main import main as app_main  # type: ignore
    app_main()
    return 0



def _ensure_qrc_resources() -> None:
    """Auto-compile and register Qt resources (.rcc) or Python .qrc modules.

    Strategy:
    1) If Qt `rcc` is available, compile qml.qrc/resource.qrc/src.qrc into
       sibling .rcc files and register them via QResource.
    2) Fallback to `pyside6-rcc` to generate Python resource modules and import.
    """
    from PySide6.QtCore import QResource

    here = Path(__file__).resolve().parent
    qrc_list = [here / 'qml.qrc', here / 'resource.qrc']
    rcc = shutil.which('rcc') or shutil.which('rcc.exe')
    pyside_rcc = (
        shutil.which('pyside6-rcc') or shutil.which('pyrcc5') or shutil.which('pyside2-rcc')
    )

    for qrc in qrc_list:
        if not qrc.exists():
            continue
        out_rcc = here / (qrc.stem + '.rcc')
        # Try compile .rcc if rcc available
        if rcc:
            try:
                if (not out_rcc.exists()) or (out_rcc.stat().st_mtime < qrc.stat().st_mtime):
                    subprocess.run([rcc, '-binary', str(qrc), '-o', str(out_rcc)], check=True)
            except Exception:
                out_rcc = None  # mark as unusable
        # Register .rcc if present
        if out_rcc and out_rcc.exists():
            QResource.registerResource(str(out_rcc))
            continue
        # Fallback: generate Python resource module
        py_mod = here / (qrc.stem + '_rc.py')
        if pyside_rcc:
            try:
                if (not py_mod.exists()) or (py_mod.stat().st_mtime < qrc.stat().st_mtime):
                    subprocess.run([pyside_rcc, str(qrc), '-o', str(py_mod)], check=True)
            except Exception:
                pass
        # Import the generated module if exists
        if py_mod.exists():
            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location(py_mod.stem, str(py_mod))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            except Exception:
                pass

def _run_minimal_ui() -> int:
    """运行最小 UI 启动器（中文注释）

    当完整应用不可用或仅需界面调试时，创建纯 UI 环境：
    - 提供 QML 引擎与图像提供者
    - 绑定设置桥与语法高亮
    - 不依赖设备与后端 API
    返回：应用事件循环的退出码
    """
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from app.ui.src.qml_bridge import Backend
    from app.ui.src.image_provider import CameraImageProvider
    from app.ui.src.settings_bridge import SettingsBridge
    from app.ui.src.highlighter import HighlighterBridge

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
    try:
        _ensure_qrc_resources()
    except Exception:
        try:
            sys.stderr.write("[warn] qrc auto-compile/register failed\n")
            sys.stderr.write(traceback.format_exc() + "\n")
        except Exception:
            pass
    provider = CameraImageProvider()
    engine.addImageProvider('camera', provider)
    settings = SettingsBridge(Path(__file__).resolve().parent.joinpath('config.json'))
    engine.rootContext().setContextProperty("settings", settings)
    backend = Backend(_DummyOrchestrator())
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("pyHighlighter", HighlighterBridge())
    # 从 ./qml/main.qml 加载 QML，避免依赖当前工作目录
    qml_path = str(Path(__file__).resolve().parent.joinpath("qml", "main.qml"))
    try:
        try:
            sys.stderr.write(f"Loading QML: {qml_path}\n")
        except Exception:
            pass
        from PySide6.QtCore import QUrl
        url = QUrl.fromLocalFile(qml_path)
        engine.load(url)
    except Exception as exc:
        sys.stderr.write(f"QML load exception: {exc}\n")
        return -1
    if not engine.rootObjects():
        # 打印 QML 警告，帮助诊断 UI 无法显示的问题
        try:
            for w in engine.warnings():
                sys.stderr.write(str(w.toString()) + "\n")
        except Exception:
            pass
        return -1
    return app.exec()


def main() -> None:
    """UI 入口函数（中文注释）

    - 自动修正 sys.path，支持在 app/ui 目录直接运行
    - 若当前工作目录为 app/ui 或传入 --minimal / --ui-only / -m，则仅启动 UI
    - 尝试启动完整应用，失败则回退到最小 UI
    """
    _ensure_project_root_on_path()
    args = set(a.lower() for a in sys.argv[1:])
    here = Path(__file__).resolve().parent
    force_minimal = ("--minimal" in args) or ("--ui-only" in args) or ("-m" in args)
    # If launched directly from app/ui as cwd with no flags, assume UI-only
    if Path.cwd().resolve() == here and not force_minimal:
        force_minimal = True
    if force_minimal:
        ret = _run_minimal_ui()
        sys.exit(ret)
    try:
        sys.exit(_run_full_app())
    except BaseException:
        # Fall back to a minimal, offline UI launcher (also captures SystemExit from app.main)
        ret = _run_minimal_ui()
        sys.exit(ret)


if __name__ == "__main__":
    main()


