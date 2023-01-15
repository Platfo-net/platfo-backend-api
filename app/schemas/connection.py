from typing import List, Optional
from pydantic import UUID4, BaseModel


class ConnectionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    application_name: Optional[str] = None
    account_id: Optional[int] = None
    details: List[dict]


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(ConnectionCreate):
    pass


class ConnectionInDBBase(ConnectionBase):
    id: int

    class Config:
        orm_mode = True


class Connection(ConnectionInDBBase):
    pass
