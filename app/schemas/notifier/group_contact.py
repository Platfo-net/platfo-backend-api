from typing import List

from pydantic import UUID4, BaseModel

from app.schemas.live_chat import Contact
from app.schemas.pagination import Pagination


class GroupContact(BaseModel):
    contact_igs_id: int
    contact_id: UUID4


class GroupContactListItem(GroupContact):
    contact: Contact

    class Config:
        orm_mode = True


class ContactSample(BaseModel):
    profile_image: str = None
    username: str = None


class CampaignContactApiSchema(BaseModel):
    items: List[ContactSample]
    pagination: Pagination
