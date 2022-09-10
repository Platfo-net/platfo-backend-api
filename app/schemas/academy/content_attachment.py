from typing import Optional

from pydantic import BaseModel, UUID4


class ContentAttachmentBase(BaseModel):
    attachment_type: Optional[str] = None
    attachment_id: Optional[str] = None


class ContentAttachmentCreate(ContentAttachmentBase):
    pass


class ContentAttachment(ContentAttachmentBase):
    id: UUID4

    class Config:
        orm_mode = True


class ContentAttachmentList(BaseModel):
    id: UUID4
    attachment_type: Optional[str] = None
    attachment_id: Optional[str] = None

    class Config:
        orm_mode = True
