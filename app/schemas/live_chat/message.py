from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class MessageBase(BaseModel):
    from_page_id: str
    to_page_id: str
    content: dict
    mid: Optional[str] = None


class MessageCreate(MessageBase):
    direction: str = None
    user_id: int = None


class Message(MessageBase):
    id: UUID4
    send_at: datetime


class MessageSend(BaseModel):
    text: Optional[str] = None
