from typing import Optional
from pydantic import UUID4, BaseModel


class Account(BaseModel):
    id: UUID4
    username: Optional[str] = None
    platform: Optional[str] = None
    profile_image: Optional[str] = None
    page_id: Optional[str] = None


class AccountDetail(BaseModel):
    id: UUID4
    username: Optional[str] = None
    platform: Optional[str] = None
    profile_image: Optional[str] = None
    page_id: Optional[str] = None
    information: Optional[dict] = None
