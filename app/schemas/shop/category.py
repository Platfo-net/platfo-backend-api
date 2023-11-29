

from typing import Optional

from pydantic import UUID4, BaseModel


class CategoryBase(BaseModel):
    title: str
    image: Optional[str] = None


class CategoryCreate(CategoryBase):
    shop_id: UUID4


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: UUID4
    image_url: Optional[str] = None
