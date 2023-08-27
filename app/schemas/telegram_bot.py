

from typing import Optional
from pydantic import BaseModel


class TelegramBotBase(BaseModel):
    app_id: str
    app_secret: str
    bot_token: str


class ConnectTelegramBot(TelegramBotBase):
    pass


class TelegramBotCreate(TelegramBotBase):
    bot_id: str
    first_name: Optional[str] = None
    username: Optional[str] = None


class TelegramBot(BaseModel):
    first_name: Optional[str] = None
    username: Optional[str] = None
