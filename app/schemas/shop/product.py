

from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination

from .category import Category


class ProductBase(BaseModel):
    title: str
    image: str
    price: float
    currency: str


class ProductCreate(ProductBase):
    category_id: UUID4
    shop_id: UUID4


class ProductUpdate(ProductBase):
    category_id: UUID4


class Product(ProductBase):
    id: UUID4
    category: Category
    created_at: datetime
    updated_at: datetime


class ProductListAPI(BaseModel):
    items: List[Product]
    pagination: Pagination
