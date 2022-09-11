from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel


class ChatflowBase(BaseModel):
    is_active: Optional[bool] = True
    name: Optional[str] = None


class ChatflowCreate(ChatflowBase):
    pass


class ChatflowUpdate(ChatflowBase):
    pass


class Chatflow(ChatflowBase):
    id: UUID4
    user_id: Optional[UUID4] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
