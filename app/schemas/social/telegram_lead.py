from typing import Optional

from pydantic import BaseModel


class TelegramLeadCreate(BaseModel):
    chat_id: int
    telegram_bot_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    lead_number: int
