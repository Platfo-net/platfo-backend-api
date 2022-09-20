

from .chatflow import Chatflow
from typing import Optional
from typing import List, Optional
from pydantic import UUID4, BaseModel
from app.schemas.account import Account


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


class ConnectionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    application_name: Optional[str] = None
    account_id: Optional[UUID4] = None
    details: List[dict]


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(ConnectionCreate):
    pass


class ConnectionInDBBase(ConnectionBase):
    id: UUID4

    class Config:
        orm_mode = True


class Connection(ConnectionInDBBase):
    pass