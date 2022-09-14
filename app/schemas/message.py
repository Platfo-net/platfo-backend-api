from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class MessageBase(BaseModel):
    from_page_id: str
    to_page_id: str
    content: dict
    mid: Optional[str] = None
    user_id: UUID4


class MessageCreate(MessageBase):
    direction: str = None


class Message(MessageBase):
    id: UUID4
    send_at: datetime


class SendMessage(BaseModel):
    text:Optional[str] = None
