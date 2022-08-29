from typing import Optional
from pydantic import UUID4, BaseModel


class CategoryBase(BaseModel):
    title: Optional[str] = None
    parent_id: Optional[UUID4] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(BaseModel):
    id: UUID4

    class Config:
        orm_mode = True
