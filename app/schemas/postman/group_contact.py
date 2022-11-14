

from pydantic import BaseModel, UUID4
from app.schemas.live_chat import Contact


class GroupContact(BaseModel):
    contact_igs_id: str
    contact_id: UUID4


class GroupContactListItem(GroupContact):
    contact: Contact

    class Config:
        orm_mode = True



class ContactSample(BaseModel):
    profile_image: str = None
    username: str = None