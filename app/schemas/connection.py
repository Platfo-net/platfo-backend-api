from typing import List, Optional
from pydantic import UUID4, BaseModel


class ConnectionChatflowBase(BaseModel):
    chatflow_id: Optional[UUID4] = None
    trigger_id: Optional[UUID4] = None


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
