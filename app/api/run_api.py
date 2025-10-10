from __future__ import annotations

import os
import signal
import sys
import threading

from pathlib import Path
_here = Path(__file__).resolve()
_project_root = _here.parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from app.core.events import EventBus
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim
from app.devices.sim.motion_sim import MotionSim
from app.process.orchestrator import Orchestrator
from app.ui.src.image_provider import CameraImageProvider
from app.api.server import create_app


def main() -> None:
    """独立启动后端 API（可调用，中文注释）。

    - 启动相机与视觉流水线（无 UI，仅为 API 提供图像）
    - 创建 FastAPI 应用并通过 uvicorn 运行
    - 端口优先读取环境变量 COPPER_API_PORT，其次读取 app/ui/config.json
    """
    bus = EventBus()
    motion = MotionSim()
    orch = Orchestrator(bus, motion)

    # Vision + camera setup (headless)
    vision = VisionPipeline(bus)
    cam = CameraSim()
    cam.open()

    provider = CameraImageProvider()

    def on_frame(frame):
        vision.on_frame(frame)
        try:
            provider.set_frame(frame)
        except Exception:
            pass

    cam.start_stream(on_frame)

    # Start FastAPI via uvicorn
    import uvicorn
    from app.config import DEBUG

    app = create_app(provider, orch, motion)

    # Graceful shutdown to stop camera
    def _stop_cam(*_):
        try:
            cam.stop_stream()
            cam.close()
        except Exception:
            pass

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _stop_cam)
        except Exception:
            pass

    port = int(os.getenv("COPPER_API_PORT", "0") or 0)
    if not port:
        try:
            from pathlib import Path
            import json
            cfg = json.loads(Path("app/ui/config.json").read_text(encoding="utf-8"))
            port = int(cfg.get("api_port", 8010))
        except Exception:
            port = 8010
    log_level = "debug" if DEBUG else "info"
    uvicorn.run(app, host="127.0.0.1", port=port, log_level=log_level)

    # Ensure camera stops after server exits
    _stop_cam()


if __name__ == "__main__":
    main()


