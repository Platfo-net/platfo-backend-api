import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Content(Base):

    __tablename__ = "contents"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    title = Column(String(1024), nullable=True)
    caption = Column(Text(), nullable=True)
    detail = Column(Text(), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    content_attachment = relationship(
        "ContentAttachment", back_populates="content", cascade="all, delete-orphan")
    content_categories = relationship(
        "ContentCategory", back_populates="content", cascade="all, delete-orphan")
