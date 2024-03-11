from typing import Optional

from pydantic import BaseModel


class TelegramLeadMessageCreate(BaseModel):
    lead_id: Optional[int] = None
    is_lead_to_bot: bool
    message: Optional[str] = None
    message_id: Optional[int] = None
    mirror_message_id: Optional[int] = None
    reply_to_id: Optional[int] = None
