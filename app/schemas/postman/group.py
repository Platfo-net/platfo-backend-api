from app.schemas.pagination import Pagination
from typing import List, Optional
from pydantic import BaseModel, UUID4
from .group_contact import GroupContact, ContactSample


class GroupBase(BaseModel):
    name: str = None
    description: str = None


class GroupCreate(GroupBase):
    facebook_page_id: str = None


class GroupUpdate(GroupBase):
    pass


class GroupCreateApiSchemas(GroupBase):
    facebook_page_id: str = None
    contacts: List[GroupContact]


class GroupUpdateApiSchemas(GroupBase):
    contacts: List[GroupContact]


class Group(GroupBase):
    id: Optional[UUID4]


class GroupContactSample(GroupBase):
    id: Optional[UUID4]
    contacts: List[ContactSample] = []


class GroupListApi(BaseModel):
    items: List[GroupContactSample]
    pagination: Pagination
