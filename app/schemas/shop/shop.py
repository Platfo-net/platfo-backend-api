

from typing import Optional

from pydantic import UUID4, BaseModel


class ShopBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_info_required: Optional[bool] = True
    color_code: Optional[str] = None


class ShopCreate(ShopBase):
    pass


class ShopUpdate(ShopBase):
    pass


class Shop(ShopBase):
    id: UUID4


class ShopConnectSupport(BaseModel):
    token: str
    shop_id: UUID4


class ShopState(BaseModel):
    is_connected_to_support_bot: bool
    is_connected_to_bot: bool
    is_connected_to_bot_verified: bool
