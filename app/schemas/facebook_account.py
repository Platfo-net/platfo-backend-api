from typing import Optional

from .user import User
from pydantic import UUID4, BaseModel


class FacebookAccountBase(BaseModel):
    facebook_user_long_lived_token: Optional[str] = None
    facebook_user_id: Optional[str] = None
    user_id: UUID4 = None


class FacebookAccountCreate(FacebookAccountBase):
    pass


class FacebookAccountUpdate(FacebookAccountBase):
    pass


class FacebookAccountInDBBase(FacebookAccountBase):
    id: UUID4
    user: Optional[User]

    class Config:
        orm_mode = True


class FacebookAccount(FacebookAccountInDBBase):
    pass


class FacebookAccountInDB(FacebookAccountInDBBase):
    pass
