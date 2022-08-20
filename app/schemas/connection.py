

from typing import List, Optional
from pydantic import UUID4, BaseModel
from app.schemas.account import Account
from app.schemas.connection_chatflow import ConnectionChatflow, \
    ConnectionChatflowCreate


class ConnectionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    application_name: Optional[str] = None
    account_id: Optional[UUID4] = None


class ConnectionCreate(ConnectionBase):
    connection_chatflows: List[ConnectionChatflowCreate]


class ConnectionUpdate(ConnectionCreate):
    pass


class ConnectionInDBBase(ConnectionBase):
    id: UUID4

    class Config:
        orm_mode = True


class Connection(ConnectionInDBBase):
    account: Optional[Account] = None


class ConnectionInDB(ConnectionInDBBase):
    connection_chatflows: List[ConnectionChatflow]
