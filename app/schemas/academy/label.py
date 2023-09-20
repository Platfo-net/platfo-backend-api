from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination


class LabelBase(BaseModel):
    name: Optional[str] = None


class LabelCreate(LabelBase):
    pass


class LabelUpdate(LabelBase):
    pass


class Label(BaseModel):
    id: UUID4

    class Config:
        from_attributes = True


class LabelInDB(LabelBase):
    id: UUID4

    class Config:
        from_attributes = True


class LabelListApi(BaseModel):
    items: List[LabelInDB]
    pagination: Pagination


class LabelListItemContent(BaseModel):
    id: UUID4
    name: Optional[str] = None

    class Config:
        from_attributes = True


class LabelContent(BaseModel):
    label_id: Optional[UUID4] = None

    class Config:
        from_attributes = True
