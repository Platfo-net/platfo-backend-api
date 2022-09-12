from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class ContactBase(BaseModel):
    contact_igs_id: str
    user_page_id: str
    user_id: UUID4


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
