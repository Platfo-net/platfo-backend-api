

from pydantic import BaseModel


class ShopPaymentMethod(BaseModel):
    shop_id: int
    payment_method_id: int


class ShopPaymentMethodCreate(BaseModel):
    pass
