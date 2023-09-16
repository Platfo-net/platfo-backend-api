from pydantic import UUID4, BaseModel


class PaymentMethodBase(BaseModel):
    title: str
    description: str


class PaymentMethodCreate(PaymentMethodBase):
    shop_id: UUID4


class PaymentMethodUpdate(PaymentMethodBase):
    shop_id: UUID4


class PaymentMethod(PaymentMethodBase):
    id: UUID4
