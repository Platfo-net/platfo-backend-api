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
    items: list = []


class PaymentMethodGroup(BaseModel):
    title: str
    items: list = []


class PaymentMethodGroupView(PaymentMethodBase):
    id: UUID4
    is_active: bool


class PaymentMethodGroupList(BaseModel):
    payment_gateway: PaymentMethodGroup
    cash: PaymentMethodGroup
