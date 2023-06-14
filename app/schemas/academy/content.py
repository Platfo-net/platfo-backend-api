from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field

from app.schemas.academy.category import (CategoryContent,
                                          CategoryListItemContent)
from app.schemas.academy.label import LabelContent, LabelListItemContent
from app.schemas.pagination import Pagination


class File(BaseModel):
    url: Optional[str] = None


class SubData(BaseModel):
    text: Optional[str] = None
    level: Optional[str] = None
    items: Optional[List] = None
    style: Optional[str] = None
    file: Optional[File] = None
    caption: Optional[str] = None
    withBorder: Optional[bool] = False
    stretched: Optional[bool] = False
    withBackground: Optional[bool] = False


class Data(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    data: Optional[SubData] = None


class ContentBase(BaseModel):
    title: Optional[str] = None
    blocks: Optional[List[Data]] = None
    caption: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_published: Optional[bool] = False
    slug: Optional[str] = None
    cover_image: Optional[str] = None
    version: Optional[str] = None
    time: Optional[str] = None


class ContentBaseList(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_published: Optional[bool] = False
    slug: Optional[str] = None
    cover_image: Optional[str] = None


class ContentCreate(ContentBase):
    categories: List[CategoryContent]
    labels: List[LabelContent]


class ContentUpdate(ContentBase):
    pass


class Content(BaseModel):
    id: UUID4

    class Config:
        orm_mode = True


class ContentInDB(ContentBase):
    id: UUID4

    class Config:
        orm_mode = True


class ContentDetailList(ContentBase):
    id: UUID4
    user_id: UUID4
    categories: List[CategoryListItemContent]
    labels: List[LabelListItemContent]

    class Config:
        orm_mode = True


class ContentDetail(BaseModel):
    content_detail: List[ContentDetailList]

    class Config:
        orm_mode = True


class ContentCategory(BaseModel):
    category: CategoryListItemContent

    class Config:
        orm_mode = True


class ContentLabel(BaseModel):
    label: LabelListItemContent

    class Config:
        orm_mode = True


class ContentListItem(ContentBaseList):
    id: UUID4
    content_categories: Optional[List[ContentCategory]] = Field(alias='categories')
    content_labels: Optional[List[ContentLabel]] = Field(alias='labels')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ContentListApi(BaseModel):
    items: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True


class ContentSearch(BaseModel):
    contents: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
