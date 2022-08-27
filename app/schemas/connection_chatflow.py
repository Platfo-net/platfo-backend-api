from typing import Optional
from pydantic import UUID4, BaseModel

# from .trigger import Trigger
from .chatflow import Chatflow


class ConnectionChatflowBase(BaseModel):
    chatflow_id: Optional[UUID4] = None
    trigger_id: Optional[UUID4] = None


class ConnectionChatflowCreate(ConnectionChatflowBase):
    pass


class ConnectionChatflow(ConnectionChatflowBase):
    id: UUID4
    chatflow: Optional[Chatflow]

    class Config:
        orm_mode = True
