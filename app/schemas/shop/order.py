from typing import List, Optional

from pydantic import UUID4, BaseModel


class OrderItemOrderCreate(BaseModel):
    product_id: UUID4
    count: int


class OrderCreate(BaseModel):
    items: List[OrderItemOrderCreate]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    payment_method_id: UUID4


class OrderCreateResponse(BaseModel):
    order_number: str


class OrderItemCreate(BaseModel):
    product_id: int
    count: int
    price: float
    currency: str


class OrderSummary(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    order_number: str
    total_amount: float
