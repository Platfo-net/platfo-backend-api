
from datetime import datetime
from typing import Optional, List

from pydantic import UUID4, BaseModel

from app.schemas.academy.category import CategoryContent, \
    CategoryListItemContent
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
        schema_extra = {
            "example": {
                "contents": [
                    {
                        "title": "مقاله تستی",
                        "blocks": [
                            {
                                "id": "1234567",
                                "type": "paragraph",
                                "data": {
                                    "text": "hello this is a sample text",
                                    "level": 'null',
                                    "items": 'null',
                                    "style": 'null',
                                    "file": 'null',
                                    "caption": 'null',
                                    "withBorder": False,
                                    "stretched": False,
                                    "withBackground": False
                                }
                            }
                        ],
                        "caption": "this is a good article",
                        "created_at": "2022-09-21T12:20:55.139295",
                        "updated_at": "2022-09-21T12:20:55.139298",
                        "is_published": 'true',
                        "version": "2.24.3",
                        "time": "1663757930863",
                        "user_id": "4c4b3ea1-ec54-4f52-bc64-409e91bd690b",
                        "slug": "مقاله-تستی",
                        "cover_image": "http://minio:9000/academy-attachment-bucket/"
                                       "a13efb7c-a36e-4c21-8eab-343f00eef94a-images.jpeg?"
                                       "X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential="
                                       "botinow%2F20220921%2Fus-east-1%2Fs3%2Faws4_request"
                                       "&X-Amz-Date=20220921T122003Z&X-Amz-Expires=86"
                                       "400&X-Amz-SignedHeaders=host&X-Amz-Signature=ef6f55"
                                       "0e1a97d13f109a92478cc00944d075f4"
                                       "0829573793dd13e4593f2c22e3",
                        "id": "a6c1bad7-9d9d-4b41-b03c-957f5715b100",
                        "content_categories": [
                            {
                                "category": {
                                    "id": "faa00882-d293-4732-86af-6418e34c337a",
                                    "title": "cat 1",
                                    "parent_id": '5e60a8ed-869a-42f3-803f-5c0cac749808'
                                }
                            }
                        ],
                        "content_labels": [
                            {
                                "label": {
                                    "id": "d390bf06-eb67-4fd1-ae64-945b3895d378",
                                    "label_name": "tagzzz"
                                }
                            }
                        ]
                    }
                ]
            }
        }


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
    content_categories: Optional[List[ContentCategory]]
    content_labels: Optional[List[ContentLabel]]

    class Config:
        orm_mode = True


class ContentListApi(BaseModel):
    contents: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                    "contents": [
                        {
                            "title": "مقاله تستی",
                            "caption": "this is a good article",
                            "created_at": "2022-09-21T12:20:55.139295",
                            "updated_at": "2022-09-21T12:20:55.139298",
                            "is_published": 'true',
                            "slug": "مقاله-تستی",
                            "cover_image": "http://minio:9000/academy-attachment-bucket/"
                                           "a13efb7c-a36e-4c21-8eab-343f00eef94a-images.jpeg?"
                                           "X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential="
                                           "botinow%2F20220921%2Fus-east-1%2Fs3%2Faws4_request"
                                           "&X-Amz-Date=20220921T122003Z&X-Amz-Expires=86"
                                           "400&X-Amz-SignedHeaders=host&X-Amz-Signature=ef6f55"
                                           "0e1a97d13f109a92478cc00944d075f4"
                                           "0829573793dd13e4593f2c22e3",
                            "id": "a6c1bad7-9d9d-4b41-b03c-957f5715b100",
                            "content_categories": [
                                {
                                    "category": {
                                        "id": "faa00882-d293-4732-86af-6418e34c337a",
                                        "title": "cat 1",
                                        "parent_id": '5e60a8ed-869a-42f3-803f-5c0cac749808'
                                    }
                                }
                            ],
                            "content_labels": [
                                {
                                    "label": {
                                        "id": "d390bf06-eb67-4fd1-ae64-945b3895d378",
                                        "label_name": "tagzzz"
                                }
                            }
                        ]
                    }
                ]
            }
        }


class ContentSearch(BaseModel):
    contents: List[ContentListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
