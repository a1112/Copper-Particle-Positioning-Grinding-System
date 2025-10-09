from dataclasses import dataclass

@dataclass
class Calibration:
    pixel_to_mm: float = 0.01
