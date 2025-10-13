from __future__ import annotations

import sys

try:
    import numpy as np
    from fastapi.testclient import TestClient
    from app.api.server import create_app
    from app.core.events import EventBus
    from app.devices.sim.motion_sim import MotionSim
    from app.process.orchestrator import Orchestrator
    from app.ui.src.image_provider import CameraImageProvider
except Exception as e:
    print(f"[SMOKE] Import error: {e}")
    sys.exit(1)


def main() -> int:
    bus = EventBus()
    motion = MotionSim()
    orch = Orchestrator(bus, motion)
    provider = CameraImageProvider()
    # seed a dummy frame
    frame = np.zeros((200, 300, 3), dtype=np.uint8)
    provider.set_frame(frame)

    app = create_app(provider, orch, motion)
    client = TestClient(app)

    r1 = client.get("/health")
    print("/health:", r1.status_code, r1.json())

    r2 = client.get("/status")
    print("/status:", r2.status_code, r2.json().get("state"))

    r3 = client.get("/image.png")
    print("/image.png:", r3.status_code, len(r3.content))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

