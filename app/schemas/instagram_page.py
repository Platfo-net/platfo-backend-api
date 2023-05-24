from typing import Optional

from pydantic import UUID4, BaseModel


class InstagramPageBase(BaseModel):
    facebook_page_id: Optional[int] = None
    facebook_page_token: str = None
    instagram_page_id: Optional[int] = None
    username: Optional[str] = None
    profile_picture_url: Optional[str] = None
    facebook_user_long_lived_token: Optional[str] = None
    facebook_user_id: Optional[str] = None

    name: Optional[str] = None
    website: Optional[str] = None
    ig_id: Optional[str] = None
    followers_count: Optional[int] = None
    follows_count: Optional[int] = None
    biography: Optional[str] = None


class InstagramPageCreate(InstagramPageBase):
    user_id: int


class InstagramPageUpdate(InstagramPageBase):
    user_id: Optional[int] = None


class InstagramPage(BaseModel):
    id: Optional[UUID4]
    facebook_page_id: Optional[int] = None
    instagram_page_id: Optional[int] = None
    username: Optional[str] = None
    profile_picture_url: Optional[str] = None

    name: Optional[str] = None
    website: Optional[str] = None
    ig_id: Optional[str] = None
    followers_count: Optional[int] = None
    follows_count: Optional[int] = None
    biography: Optional[str] = None


class ConnectPage(BaseModel):
    facebook_user_id: int
    facebook_user_token: str
