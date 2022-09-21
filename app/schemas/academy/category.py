
from typing import Optional, List

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
        orm_mode = True


class CategoryContent(BaseModel):
    category_id: Optional[UUID4] = None

    class Config:
        orm_mode = True


class CategoryListItemContent(BaseModel):
    id: UUID4
    title: Optional[str] = None
    parent_id: Optional[UUID4] = None

    class Config:
        orm_mode = True


class CategoryListItem(BaseModel):
    id: UUID4
    title: Optional[str] = None
    parent_id: Optional[UUID4] = None
    children: Optional[List[dict]] = None

    class Config:
        orm_mode = True


class CategoryListApi(BaseModel):
    categories: List[CategoryListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "categories": [
                    {
                        "title": "guide",
                        "parent_id": "null",
                        "children": [
                            {"id": "0cabbc9b-bed2-4d83-924b-748c4c4394af",
                             "title": "guide instagram",
                             "children": [],
                             "parent_id": "0244e0b0-e498-407a-95e1-25fd486fa527"}  # noqa
                        ],
                        "id": "e744f7eb-3529-4562-bcf3-e8e4eaad0267"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "total_pages": 1,
                    "page_size": 20,
                    "total_count": 4
                }
            }
        }
