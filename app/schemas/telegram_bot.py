

from typing import Optional

from pydantic import UUID4, BaseModel


class TelegramBotBase(BaseModel):
    bot_token: str


class ConnectTelegramBot(TelegramBotBase):
    pass


class TelegramBotCreate(TelegramBotBase):
    bot_id: str
    first_name: Optional[str] = None
    username: Optional[str] = None


class TelegramBotUpdate(TelegramBotBase):
    welcome_message: Optional[str] = None


class TelegramBot(BaseModel):
    id: UUID4
    first_name: Optional[str] = None
    username: Optional[str] = None
    welcome_message: Optional[str] = None
