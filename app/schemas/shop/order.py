from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination

from .table import Table


class OrderItemOrderCreate(BaseModel):
    product_id: UUID4
    count: int
    variant_id: Optional[UUID4] = None


class OrderBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemOrderCreate]
    payment_method_id: UUID4
    shipment_method_id: UUID4
    table_id: Optional[UUID4] = None


class OrderCreateResponse(BaseModel):
    order_number: str


class OrderItem(BaseModel):
    product_id: int
    count: int
    price: float
    currency: str
    variant_title: Optional[str] = None
    product_title: str
    variant_id: Optional[int] = None


class OrderListItem(BaseModel):
    id: UUID4
    order_number: int
    total_amount: float
    currency: str
    created_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    payment_method: Optional[str] = None
    shipment_method: Optional[str] = None
    status: Optional[str] = None
    table: Optional[Table] = None


class OrderListApiResponse(BaseModel):
    items: List[OrderListItem]
    pagination: Pagination


class OrderItemResponse(BaseModel):
    count: int
    price: float
    currency: str
    variant_title: Optional[str] = None
    product_title: str
    image: Optional[str]


class Order(OrderBase):
    id: UUID4
    total_amount: float
    currency: str
    items: List[OrderItemResponse]
    payment_method: Optional[str] = None
    shipment_method: Optional[str] = None
    status: Optional[str] = None
    payment_information: Optional[dict] = None
    table: Optional[Table] = None
    shipment_cost_amount : Optional[float] = None
    shipment_cost_currency : Optional[str] = None


class OrderChangeStatus(BaseModel):
    status: str
