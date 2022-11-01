from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel

from app.schemas.pagination import Pagination


class ContactBase(BaseModel):
    contact_igs_id: str
    user_page_id: str
    user_id: UUID4
    comment_count: int = 0
    message_count: int = 0
    live_comment_count: int = 0
    first_impression: str = None


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: UUID4
    last_message_at: datetime
    information: Optional[dict] = None
    last_message: dict


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
    contacts: List[Contact]
    pagination: Pagination
