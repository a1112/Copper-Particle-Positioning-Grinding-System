from app.core.events import EventBus, TOPIC_TARGET_FOUND
from app.vision.detector import Detector

class VisionPipeline:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.detector = Detector()

    def on_frame(self, frame):
        res = self.detector.locate(frame)
        if res:
            x, y, th, score = res
            try:
                h, w = frame.shape[:2]
            except Exception:
                h, w = 0, 0
            self.bus.publish(TOPIC_TARGET_FOUND, dict(x=x, y=y, theta=th, score=score, width=w, height=h))
