from typing import Optional

from pydantic import UUID4, BaseModel


class InstagramPageBase(BaseModel):
    facebook_page_id: Optional[str] = None
    facebook_page_token: str = None
    instagram_page_id: Optional[str] = None
    instagram_username: Optional[str] = None
    instagram_profile_picture_url: Optional[str] = None
    information: Optional[dict] = None
    facebook_user_long_lived_token: Optional[str] = None
    facebook_user_id: Optional[str] = None
    user_id: UUID4


class InstagramPageCreate(InstagramPageBase):
    pass


class InstagramPageUpdate(InstagramPageBase):
    pass


class InstagramPageInDBBase(InstagramPageBase):
    id: Optional[UUID4]

    class Config:
        orm_mode = True


class InstagramPage(InstagramPageInDBBase):
    pass


class InstagramPageInDB(InstagramPageInDBBase):
    pass


class ConnectPage(BaseModel):
    facebook_user_id: str
    facebook_user_token: str
