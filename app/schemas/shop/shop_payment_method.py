

from typing import Optional

from pydantic import UUID4, BaseModel


class ShopPaymentMethodBase(BaseModel):
    shop_id: int
    payment_method_id: int


class ShopPaymentMethodCreate(BaseModel):
    pass


class ChangePaymentIsActive(BaseModel):
    is_active: bool


class EditPaymentInformation(BaseModel):
    information: dict


class ShopPaymentMethod(BaseModel):
    title: str
    description: str
    id: UUID4
    information: Optional[dict] = None
    is_active: bool
