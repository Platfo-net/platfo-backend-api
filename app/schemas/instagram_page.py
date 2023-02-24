from typing import Optional

from pydantic import UUID4, BaseModel


class InstagramPageBase(BaseModel):
    facebook_page_id: Optional[int] = None
    facebook_page_token: str = None
    instagram_page_id: Optional[int] = None
    username: Optional[str] = None
    profile_picture_url: Optional[str] = None
    information: Optional[dict] = None
    facebook_user_long_lived_token: Optional[str] = None
    facebook_user_id: Optional[str] = None


class InstagramPageCreate(InstagramPageBase):
    user_id: int


class InstagramPageUpdate(InstagramPageBase):
    user_id: int


class InstagramPageInDBBase(InstagramPageBase):
    id: Optional[UUID4]

    class Config:
        orm_mode = True


class InstagramPage(BaseModel):
    id: Optional[UUID4]
    facebook_page_id: Optional[int] = None
    instagram_page_id: Optional[int] = None
    username: Optional[str] = None
    profile_picture_url: Optional[str] = None
    information: Optional[dict] = None


class InstagramPageInDB(InstagramPageInDBBase):
    pass


class ConnectPage(BaseModel):
    facebook_user_id: int
    facebook_user_token: str
