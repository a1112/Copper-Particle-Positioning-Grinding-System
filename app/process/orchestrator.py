from app.core.state_machine import StateMachine, ProcState
from app.core.events import EventBus, TOPIC_TARGET_FOUND
from app.devices.motion_base import IMotionController

class Orchestrator:
    def __init__(self, bus: EventBus, motion: IMotionController):
        self.bus = bus
        self.sm = StateMachine()
        self.motion = motion
        self.target = None
        self.bus.subscribe(TOPIC_TARGET_FOUND, self._on_target)
        self._wire()

    def _on_target(self, payload):
        self.target = payload
        self.sm.state = ProcState.MOVE
        # also push to UI backend if available
        try:
            if hasattr(self, 'backend'):
                self.backend.set_target(payload.get('x', -1.0), payload.get('y', -1.0), payload.get('theta', 0.0), payload.get('score', 0.0))
        except Exception:
            pass

    def _wire(self):
        self.sm.on(ProcState.IDLE, self._idle)
        self.sm.on(ProcState.MOVE, self._move)

    def _idle(self):
        pass

    def _move(self):
        if self.target:
            self.motion.move_abs(self.target['x'], self.target['y'])
            self.motion.wait_done()
            self.sm.state = ProcState.PREGRIND
