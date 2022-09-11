from typing import Optional

from .facebook_account import FacebookAccount
from pydantic import UUID4, BaseModel


class InstagramPageBase(BaseModel):
    facebook_account_id: Optional[UUID4] = None
    facebook_page_id: Optional[str] = None
    facebook_page_token: str = None
    instagram_page_id: Optional[str] = None
    instagram_username: Optional[str] = None
    instagram_profile_picture_url: Optional[str] = None
    information: Optional[dict] = None


class InstagramPageCreate(InstagramPageBase):
    pass


class InstagramPageUpdate(InstagramPageBase):
    pass


class InstagramPageInDBBase(InstagramPageBase):
    id: Optional[UUID4]
    facebook_account: Optional[FacebookAccount]

    class Config:
        orm_mode = True


class InstagramPage(InstagramPageInDBBase):
    pass


class InstagramPageInDB(InstagramPageInDBBase):
    pass


class ConnectPage(BaseModel):
    facebook_user_id: str
    facebook_user_token: str
