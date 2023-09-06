from pydantic import BaseModel


class TelegramLeadCreate(BaseModel):
    chat_id: int
    telegram_bot_id: int
