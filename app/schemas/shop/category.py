

from pydantic import UUID4, BaseModel


class CategoryBase(BaseModel):
    title: str


class CategoryCreate(CategoryBase):
    shop_id: UUID4


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: UUID4
