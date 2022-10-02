
from datetime import datetime
from typing import Optional, List

from pydantic import UUID4, BaseModel


class ChatroomBase(BaseModel):
    room_name: Optional[str] = None
    chat_members: Optional[List[dict]] = None


class ChatroomCreate(ChatroomBase):
    pass


class ChatroomUpdate(ChatroomBase):
    pass


class Chatroom(ChatroomBase):
    id: UUID4
    user_id: Optional[UUID4] = None
    created_at: datetime

    class Config:
        orm_mode = True
