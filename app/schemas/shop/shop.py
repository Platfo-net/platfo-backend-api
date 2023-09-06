

from typing import Optional

from pydantic import UUID4, BaseModel


class ShopBase(BaseModel):
    title: str
    description: Optional[str]
    category: Optional[str]


class ShopCreate(ShopBase):
    pass


class ShopUpdate(ShopBase):
    pass


class Shop(ShopBase):
    id: UUID4


class ShopConnectSupport(BaseModel):
    token: str
    shop_id: UUID4
