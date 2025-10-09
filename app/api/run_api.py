from __future__ import annotations

import os
import signal
import sys
import threading

from app.core.events import EventBus
from app.vision.pipeline import VisionPipeline
from app.devices.sim.camera_sim import CameraSim
from app.devices.sim.motion_sim import MotionSim
from app.process.orchestrator import Orchestrator
from app.ui.image_provider import CameraImageProvider
from app.api.server import create_app


def main() -> None:
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

    port = int(os.getenv("COPPER_API_PORT", "8010"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

    # Ensure camera stops after server exits
    _stop_cam()


if __name__ == "__main__":
    main()

