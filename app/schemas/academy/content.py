
from datetime import datetime
from typing import Optional, List

from pydantic import UUID4, BaseModel

from app.schemas.academy.category import CategoryContent, \
    CategoryListItemContent
from app.schemas.academy.content_attachment import ContentAttachment, \
    ContentAttachmentCreate
from app.schemas.academy.label import LabelListItemContent, \
    LabelContent
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
    is_published: Optional[bool] = False
    slug: Optional[str] = None
    cover_image: Optional[str] = None
    version: Optional[str] = None
    time: Optional[str] = None


class ContentCreate(ContentBase):
    content_attachments: List[ContentAttachmentCreate]
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
    content_attachments: List[ContentAttachment]

    class Config:
        orm_mode = True


class ContentDetail(BaseModel):
    content_detail: List[ContentDetailList]

    class Config:
        orm_mode = True
        # schema_extra = {
        #     "example":
        #         {
        #             "content_detail": [
        #                 {
        #                     "title": "instagram",
        #                     "detail": "this is a post about how to use instagram",
        #                     "caption": "this is a post to indlfndlvfd;k;ldkf",
        #                     "created_at": "2022-09-04T13:08:33.266774",
        #                     "id": "bb5b3d0d-4222-412d-aa13-e7bdaf5e14b3",
        #                     "categories": [
        #                         {
        #                             "id": "496d30b6-9519-4b8a-91cf-1bb1f9c48ba1",
        #                             "title": "cat 1",
        #                             "parent_id": "7bda49e9-7479-41ee-b9f4-2998bdd717a2",
        #                             "children": [
        #                                 {
        #                                     "id": "0cabbc9b-bed2-4d83-924b-748c4c4394af",
        #                                     "title": "guide instagram",
        #                                     "children": [],
        #                                     "parent_id": "0244e0b0-e498-407a-95e1-25fd486fa527"
        #                                 }
        #                             ]
        #                         }
        #                     ],
        #                     "content_attachments": [
        #                         {
        #                             "attachment_type": "jpg",
        #                             "attachment_id": "string",
        #                             "id": "111238c2-b42c-41f0-832e-58a52f45d3d8"
        #                         }
        #                     ]
        #                 }
        #             ]
        #         }
        # }


class ContentCategory(BaseModel):
    category: CategoryListItemContent

    class Config:
        orm_mode = True


class ContentLabel(BaseModel):
    label: LabelListItemContent

    class Config:
        orm_mode = True


class ContentListItem(ContentBase):
    id: UUID4
    content_categories: Optional[List[ContentCategory]]
    content_labels: Optional[List[ContentLabel]]
    # content_attachments: List[ContentAttachment]

    class Config:
        orm_mode = True


class ContentListApi(BaseModel):
    contents: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
        # schema_extra = {
        #     "example": {
        #         "contents": [
        #             {
        #                 "title": "welcome to botinow",
        #                 "detail": "this is a post about how to use instagram",
        #                 "caption": "this is a post",
        #                 "created_at": "2022-09-10T11:21:27.768557",
        #                 "id": "4be38586-9552-406b-8e6a-06c1f3773bec",
        #                 "content_categories": [
        #                     {
        #                         "category": {
        #                             "id": "c2709ad4-db44-4e49-9d2e-93c9e6ad27e3",
        #                             "title": "amozesh",
        #                             "parent_id": "null"
        #                         }
        #                     }
        #                 ]
        #             },
        #             {
        #                 "title": "content 1",
        #                 "detail": "this is a test",
        #                 "caption": "null",
        #                 "created_at": "2022-09-10T11:21:27.768557",
        #                 "id": "bb5b3d0d-4222-412d-aa13-e7bdaf5e14b3",
        #                 "content_categories": [
        #                     {
        #                         "category": {
        #                             "id": "496d30b6-9519-4b8a-91cf-1bb1f9c48ba1",
        #                             "title": "cat 1",
        #                             "parent_id": "7bda49e9-7479-41ee-b9f4-2998bdd717a2"
        #                         }
        #                     }
        #                 ]
        #             },
        #         ]
        #     }
        # }


class ContentSearch(BaseModel):
    contents: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
        # schema_extra = {
        #     "example": {
        #         "contents": [
        #             {
        #                 "title": "instagram",
        #                 "detail": "this is a post about how to use instagram",
        #                 "caption": "this is a post",
        #                 "created_at": "2022-09-05T08:16:48.774009",
        #                 "id": "dcde30d7-f87c-4105-b2f2-007cfa1588f0"
        #             }
        #         ],
        #         "pagination": {
        #             "page": 1,
        #             "total_pages": 1,
        #             "page_size": 20,
        #             "total_count": 4
        #         }
        #     }
        # }
