from typing import Optional, List

from pydantic import BaseModel

from app.schemas.pagination import Pagination


class TelegramLeadBase(BaseModel):
    chat_id: int
    telegram_bot_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    lead_number: int


class TelegramLeadCreate(TelegramLeadBase):
    pass


class TelegramLead(TelegramLeadBase):
    pass


class TelegramLeadListItem(BaseModel):
    items: List[TelegramLead]
    pagination: Pagination
