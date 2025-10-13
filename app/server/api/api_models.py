from pydantic import BaseModel


class MotionSpeed(BaseModel):
    v_fast: float
    v_work: float


class JogCmd(BaseModel):
    axis: str
    direction: int
    speed: float = 10.0


class GroupCreate(BaseModel):
    serial: str
    note: str | None = None