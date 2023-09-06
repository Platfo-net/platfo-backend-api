

from typing import Optional

from pydantic import UUID4, BaseModel


class ShopTelegramBotCreate(BaseModel):
    support_token: str
    support_bot_token: str
    shop_id: int


class ShopTelegramBotRegister(BaseModel):
    id: UUID4
    title: str
    description: Optional[str]
    category: Optional[str]
    support_token: str


class ShopConnectTelegramBot(BaseModel):
    bot_id: UUID4
    shop_id: UUID4
