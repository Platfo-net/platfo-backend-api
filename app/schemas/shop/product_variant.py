from typing import Optional

from pydantic import UUID4, BaseModel


class Variant(BaseModel):
    id: UUID4
    title: Optional[str]
    price: Optional[str]
    currency: Optional[str]
    is_available: Optional[bool] = True


class VariantCreate(BaseModel):
    title: Optional[str]
    price: Optional[str]
    currency: Optional[str]
    is_available: Optional[bool] = True
