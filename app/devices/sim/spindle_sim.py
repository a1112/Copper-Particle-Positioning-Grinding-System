from app.devices.spindle_base import ISpindle

class SpindleSim(ISpindle):
    def __init__(self):
        self._rpm = 0

    def set_rpm(self, rpm: int) -> None:
        self._rpm = rpm

    def start(self) -> None:
        pass

    def stop(self) -> None:
        self._rpm = 0

    def temperature(self) -> float:
        return 30.0

    def rpm_actual(self) -> int:
        return self._rpm
