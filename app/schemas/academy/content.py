
from typing import Optional, List
from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination


class ContentBase(BaseModel):
    title: Optional[str] = None
    detail: Optional[str] = None


class ContentCreate(ContentBase):
    pass


class ContentUpdate(ContentBase):
    pass


class Content(BaseModel):
    id: UUID4

    class Config:
        orm_mode = True


class ContentListItem(ContentBase):
    id: UUID4

    class Config:
        orm_mode = True


class ContentListApi(BaseModel):
    items: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
