

from pydantic import UUID4, BaseModel


class CategoryBase(BaseModel):
    title: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: UUID4
