from typing import Optional
from pydantic import BaseModel


class TelegramLeadMessageCreate(BaseModel):
    lead_id: int
    is_lead_to_bot: bool
    message: str
    message_id: int
    mirror_message_id: int
    reply_to_id: Optional[int] = None
