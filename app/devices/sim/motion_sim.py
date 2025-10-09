import time
from app.devices.motion_base import IMotionController

class MotionSim:
    def __init__(self):
        self.pos = [0.0, 0.0, 0.0, 0.0]

    def home(self):
        self.pos = [0.0, 0.0, 0.0, 0.0]
        time.sleep(0.1)

    def move_abs(self, x: float, y: float, z: float = 0.0, theta: float = 0.0):
        self.pos = [x, y, z, theta]
        time.sleep(0.1)

    def wait_done(self, timeout: float = 5.0) -> bool:
        return True

    def status(self):
        return tuple(self.pos)

    def set_soft_limits(self, xmin: float, xmax: float, ymin: float, ymax: float):
        pass
