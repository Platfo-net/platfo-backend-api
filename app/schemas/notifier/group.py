from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination

from .group_contact import ContactSample


class GroupBase(BaseModel):
    name: str = None
    description: str = None


class GroupCreate(GroupBase):
    facebook_page_id: int = None


class GroupUpdate(GroupBase):
    pass


class GroupCreateApiSchemas(GroupBase):
    facebook_page_id: int = None
    contacts: List[UUID4]


class GroupUpdateApiSchemas(GroupBase):
    contacts: List[UUID4]


class Group(GroupBase):
    id: Optional[UUID4]


class GroupContactSample(GroupBase):
    id: Optional[UUID4]
    contacts: List[ContactSample] = []


class GroupListApi(BaseModel):
    items: List[Group]
    pagination: Pagination


class GroupContactCreate(BaseModel):
    contact_id: Optional[int]
    contact_igs_id: Optional[int]
