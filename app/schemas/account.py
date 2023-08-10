from typing import Optional

from pydantic import UUID4, BaseModel


class Account(BaseModel):
    id: UUID4
    username: Optional[str] = None
    platform: Optional[str] = None
    profile_image: Optional[str] = None
    facebook_page_id: Optional[int] = None


class AccountDetail(BaseModel):
    id: UUID4
    username: Optional[str] = None
    platform: Optional[str] = None
    profile_image: Optional[str] = None
    facebook_page_id: Optional[int] = None

    name : Optional[str] = None
    website: Optional[str] = None
    followers_count : Optional[int] = None
    follows_count : Optional[int] = None
    biography: Optional[str] = None
