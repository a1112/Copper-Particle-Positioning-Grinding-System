from __future__ import annotations

import signal
import uvicorn

from app.core.events import EventBus
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim
from app.devices.sim.motion_sim import MotionSim
from app.process.orchestrator import Orchestrator
from app.ui.src.image_provider import CameraImageProvider
from app.api.server import create_app
from app.api.utils.logs import attach_root_handler, push
from app.diagnostics.logging import get_logger
from app.server import CONFIG


def main() -> None:
    # Attach buffer handler before producing logs
    attach_root_handler()
    log = get_logger("cli")

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

    app = create_app(provider, orch, motion)

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

    try:
        log.info("API starting at %s:%s", CONFIG.app_host, CONFIG.app_port)
        push("INFO", "api", f"Starting at {CONFIG.app_host}:{CONFIG.app_port}")
    except Exception:
        pass

    uvicorn.run(app, host=CONFIG.app_host, port=CONFIG.app_port, log_level=CONFIG.log_level)

    # Ensure camera stops after app exits
    _stop_cam()


if __name__ == "__main__":
    main()
