

from app.schemas.pagination import Pagination
from typing import List
from pydantic import UUID4, BaseModel


class InvoiceCreateAPI(BaseModel):
    plan_id: UUID4


class InvoiceBase(BaseModel):
    amount: float
    currency: str
    bought_on_discount: bool = False

    plan_name: str
    module: str
    extend_days: int
    extend_count: int


class InvoiceCreate(InvoiceBase):
    plan_id: int
    user_id: int


class Invoice(InvoiceBase):
    id: UUID4

    class Config:
        orm_mode = True


class InvoiceListItem(BaseModel):
    id: UUID4
    amount: float
    currency: str
    plan_name: str
    status: str
    module: str

    class Config:
        orm_mode = True


class InvoiceList(BaseModel):
    items: List[InvoiceListItem]
    pagination: Pagination
