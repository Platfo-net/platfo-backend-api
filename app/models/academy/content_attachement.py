from uuid import uuid4

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ContentAttachment(Base):
    __tablename__ = "content_attachments"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    attachment_type = Column(String(256), nullable=True)
    attachment_id = Column(String(256), nullable=True)

    content_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contents.id"),
        nullable=True,
    )

    content = relationship("Content", back_populates="content_attachment")
