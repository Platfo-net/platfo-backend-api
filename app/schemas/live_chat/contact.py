from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination


class ContactBase(BaseModel):
    contact_igs_id: int
    facebook_page_id: int
    first_impression: str = None


class ContactCreate(ContactBase):
    user_id: int
    last_interaction_at: datetime = None
    last_message: str = None
    last_message_at: datetime = None


class Contact(ContactBase):
    id: UUID4
    last_message_at: datetime = None
    last_interaction_at: datetime = None
    last_message: str = None
    profile_image: str = None
    username: str = None


class ProfileCreate(BaseModel):
    username: Optional[str] = None
    profile_image: Optional[str] = None


class ProfileUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None


class SearchItem(BaseModel):
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[int] = None


class ContactList(BaseModel):
    items: List[Contact]
    pagination: Pagination
