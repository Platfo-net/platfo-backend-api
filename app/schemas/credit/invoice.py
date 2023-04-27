

from app.schemas.pagination import Pagination
from typing import List
from pydantic import UUID4, BaseModel
from .plan import Plan


class InvoiceCreateAPI(BaseModel):
    plan_id: UUID4


class InvoiceCreate(BaseModel):
    plan_id: int
    user_id: int
    amount: float
    currency: str
    bought_on_discount: bool = False


class Invoice(BaseModel):
    id: UUID4
    plan_id: int
    amount: float
    currency: str
    bought_on_discount: bool = False

    plan: Plan

    class Config:
        orm_mode = True


class InvoiceListItem(BaseModel):
    id: UUID4
    amount: float
    currency: str
    plan_name: str
    status: str

    class Config:
        orm_mode = True


class InvoiceList(BaseModel):
    items: List[InvoiceListItem]
    pagination: Pagination
