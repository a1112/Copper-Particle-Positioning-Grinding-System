from __future__ import annotations

import signal
import uvicorn

from app.core.events import EventBus
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim
from app.ui.src.image_provider import CameraImageProvider
from api.api_core import app
import CONFIG
import init


def main() -> None:
    bus = EventBus()

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

    uvicorn.run(app, host=CONFIG.app_host, port=CONFIG.app_port, log_level=CONFIG.log_level)

    # Ensure camera stops after app exits
    _stop_cam()


if __name__ == "__main__":
    main()


