from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination


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
        from_attributes = True


class CategoryContent(BaseModel):
    category_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


class CategoryListItemContent(BaseModel):
    id: UUID4
    title: Optional[str] = None
    parent_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


class CategoryListItem(BaseModel):
    id: UUID4
    title: Optional[str] = None
    parent_id: Optional[UUID4] = None
    children: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class CategoryListApi(BaseModel):
    items: List[CategoryListItem]
    pagination: Pagination

    class Config:
        from_attributes = True
