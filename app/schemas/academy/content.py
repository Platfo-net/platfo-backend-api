
from typing import Optional, List
from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination
from app.schemas.academy.content_attachment import ContentAttachment,\
    ContentAttachmentCreate
from app.schemas.academy.category import CategoryContent,\
    CategoryListItem


class ContentBase(BaseModel):
    title: Optional[str] = None
    detail: Optional[str] = None


class ContentCreate(ContentBase):
    content_attachments: List[ContentAttachmentCreate]
    categories: List[CategoryContent]


class ContentUpdate(ContentBase):
    pass


class Content(BaseModel):
    id: UUID4

    class Config:
        orm_mode = True


class ContentDetailList(ContentBase):
    id: UUID4
    categories: List[CategoryListItem]
    content_attachments: List[ContentAttachment]

    class Config:
        orm_mode = True


class ContentDetail(BaseModel):
    content_detail: List[ContentDetailList]

    class Config:
        orm_mode = True


class ContentInDB(ContentBase):
    id: UUID4

    class Config:
        orm_mode = True


class ContentCategory(BaseModel):
    category_id: UUID4
    category: CategoryListItem

    class Config:
        orm_mode = True


class ContentListItem(ContentBase):
    id: UUID4
    content_categories: List[ContentCategory]

    class Config:
        orm_mode = True


class ContentListApi(BaseModel):
    items: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
