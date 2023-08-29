

from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination

from .category import Category


class ProductBase(BaseModel):
    title: str
    image: str
    price: str
    currency: str
    category_id: UUID4


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase):
    id: UUID4
    catgory: Category
    created_at : datetime
    updated_at : datetime


class ProductListAPI(BaseModel):
    items: List[Product]
    pagination: Pagination
