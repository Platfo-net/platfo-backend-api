
from typing import Optional, List

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination


class LabelBase(BaseModel):
    label_name: Optional[str] = None


class LabelCreate(LabelBase):
    pass


class LabelUpdate(LabelBase):
    pass


class Label(BaseModel):
    id: UUID4

    class Config:
        orm_mode = True


class LabelInDB(LabelBase):
    id: UUID4

    class Config:
        orm_mode = True


class LabelListApi(BaseModel):
    labels: List[LabelInDB]
    pagination: Pagination


class LabelListItemContent(BaseModel):
    id: UUID4
    label_name: Optional[str] = None

    class Config:
        orm_mode = True


class LabelContent(BaseModel):
    label_id: Optional[UUID4] = None

    class Config:
        orm_mode = True
