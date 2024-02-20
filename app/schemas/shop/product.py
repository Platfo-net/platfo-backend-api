

from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination

from .attribute import Attribute, AttributeCreate, AttributeUpdate
from .category import Category
from .product_variant import Variant, VariantCreate


class ProductBase(BaseModel):
    title: str
    image: Optional[str] = None
    price: float
    currency: str


class ProductCreate(ProductBase):
    category_id: Optional[UUID4] = None
    shop_id: Optional[UUID4] = None
    attributes: Optional[List[AttributeCreate]] = None
    variants: Optional[List[VariantCreate]] = None


class ProductUpdate(ProductBase):
    category_id: Optional[UUID4] = None
    attributes: Optional[List[AttributeUpdate]] = None
    variants: Optional[List[VariantCreate]] = None


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
