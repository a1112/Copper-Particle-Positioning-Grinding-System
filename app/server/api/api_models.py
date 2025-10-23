from typing import Any, Dict

from pydantic import BaseModel, Field


class ControlCommandPayload(BaseModel):
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)


class GroupCreate(BaseModel):
    serial: str
    note: str | None = None
