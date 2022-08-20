from typing import Optional
from pydantic import UUID4, BaseModel

from app.schemas.trigger import Trigger


class ConnectionChatflowCreate(BaseModel):
    chatflow_id: Optional[UUID4] = None
    trigger_id: Optional[UUID4] = None


class ConnectionChatflow(BaseModel):
    id: UUID4
    chatflow_id: Optional[UUID4] = None
    trigger_id: Optional[UUID4] = None
    trigger: Trigger

    class Config:
        orm_mode = True
