

from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination

from .category import Category


class ProductBase(BaseModel):
    title: str
    image: str
    price: float
    currency: str


class ProductCreate(ProductBase):
    category_id: Optional[UUID4] = None
    shop_id: Optional[UUID4] = None


class ProductUpdate(ProductBase):
    category_id: Optional[UUID4] = None


class Product(ProductBase):
    id: UUID4
    category: Optional[Category]
    created_at: datetime
    updated_at: datetime


class ProductListAPI(BaseModel):
    items: List[Product]
    pagination: Pagination
