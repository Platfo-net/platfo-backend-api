import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Content(Base):
    __tablename__ = "contents"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    title = Column(String(1024), nullable=True)
    caption = Column(Text(), nullable=True)
    detail = Column(Text(), nullable=True)
    slug = Column(String(300), unique=True)
    is_published = Column(Boolean(), default=False)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=False,
        nullable=True,
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    content_attachment = relationship(
        "ContentAttachment",
        back_populates="content",
        cascade="all, delete-orphan"
    )
    content_categories = relationship(
        "ContentCategory",
        back_populates="content",
        cascade="all, delete-orphan"
    )
    content_labels = relationship(
        "ContentLabel",
        back_populates="content",
        cascade="all, delete-orphan"
    )
    user = relationship(
        "User", back_populates="content")
