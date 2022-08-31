
from typing import Optional, List
from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination


class CategoryBase(BaseModel):
    title: Optional[str] = None
    parrent_id: Optional[UUID4] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(BaseModel):
    id: UUID4

    class Config:
        orm_mode = True


class CategoryListItem(CategoryBase):
    id: UUID4

    class Config:
        orm_mode = True


class CategoryListApi(BaseModel):
    items: List[CategoryListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
