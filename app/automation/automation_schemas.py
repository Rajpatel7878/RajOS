from pydantic import BaseModel
from datetime import datetime


class AutomationCreate(BaseModel):

    name: str
    trigger: str
    action: str


class AutomationUpdate(BaseModel):

    name: str | None = None
    trigger: str | None = None
    action: str | None = None
    enabled: bool | None = None


class AutomationResponse(BaseModel):

    id: int
    name: str
    trigger: str
    action: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AutomationEvent(BaseModel):

    type: str
    message: str | None = None
