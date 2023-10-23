from typing import Optional

from pydantic import UUID4, BaseModel


class PaymentMethodBase(BaseModel):
    title: str
    description: str


class PaymentMethodCreate(PaymentMethodBase):
    information_fields: dict
    payment_fields: dict


class PaymentMethodUpdate(PaymentMethodBase):
    pass


class PaymentMethod(PaymentMethodBase):
    id: UUID4
    information_fields: dict
    information: Optional[dict] = None
    is_active: bool
