from typing import List, Optional

from pydantic import UUID4, BaseModel


class ConnectionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    application_name: Optional[str] = None
    details: List[dict]


class ConnectionCreate(ConnectionBase):
    account_id: Optional[UUID4] = None
    platform: str


class ConnectionUpdate(ConnectionCreate):
    pass


class ConnectionInDBBase(ConnectionBase):
    id: UUID4
    account_id: Optional[UUID4] = None

    class Config:
        orm_mode = True


class Connection(ConnectionInDBBase):
    pass
