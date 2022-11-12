

from app.schemas.pagination import Pagination
from typing import List
from pydantic import BaseModel
from .group_contact import GroupContact


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
    pass


class GroupListApi(BaseModel):
    items: List[Group]
    pagination: Pagination
