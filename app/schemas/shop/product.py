

from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination

from .attribute import Attribute, AttributeCreate, AttributeUpdate
from .product_variant import VariantCreate, Variant
from .category import Category


class ProductBase(BaseModel):
    title: str
    image: Optional[str] = None
    price: float
    currency: str


class ProductCreate(ProductBase):
    category_id: Optional[UUID4] = None
    shop_id: Optional[UUID4] = None
    attributes: List[AttributeCreate] = []
    variants: List[VariantCreate]


class ProductUpdate(ProductBase):
    category_id: Optional[UUID4] = None
    attributes: List[AttributeUpdate]
    variants: List[VariantCreate]


class Product(ProductBase):
    id: UUID4
    category: Optional[Category]
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str] = None
    attributes: Optional[List[Attribute]] = None
    variants: Optional[List[Variant]] = None


class ProductListAPI(BaseModel):
    items: List[Product]
    pagination: Pagination
