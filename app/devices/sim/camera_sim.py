import numpy as np
import time
from threading import Thread, Event
from app.devices.camera_base import FrameCallback

class CameraSim:
    def __init__(self):
        self._t: Thread | None = None
        self._stop = Event()

    def open(self): pass
    def close(self): self.stop_stream()

    def start_stream(self, cb: FrameCallback):
        self._stop.clear()
        def run():
            while not self._stop.is_set():
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cb(frame)
                time.sleep(0.05)
        self._t = Thread(target=run, daemon=True)
        self._t.start()

    def stop_stream(self):
        self._stop.set()
        if self._t:
            self._t.join(timeout=1)
            self._t = None

    def set_param(self, key: str, value):
        pass
