from typing import Optional

from pydantic import BaseModel, UUID4


class ContentAttachmentBase(BaseModel):
    attachment_id: Optional[str] = None


class ContentAttachment(ContentAttachmentBase):
    id: UUID4

    class Config:
        orm_mode = True
