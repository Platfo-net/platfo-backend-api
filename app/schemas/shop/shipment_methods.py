from typing import Optional
from pydantic import UUID4, BaseModel


class ShipmentMethodBase(BaseModel):
    title: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None


class ShipmentMethodCreate(ShipmentMethodBase):
    shop_id: UUID4


class ShipmentMethodUpdate(ShipmentMethodBase):
    shop_id: UUID4


class ShipmentMethod(ShipmentMethodBase):
    id: UUID4
    is_active: bool


class ChangeShipmentIsActive(BaseModel):
    is_active: bool
