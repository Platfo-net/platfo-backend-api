
import datetime
from uuid import uuid4

from slugify import slugify

from sqlalchemy import event
from sqlalchemy import Column, String, Text,\
    DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Content(Base):
    __tablename__ = "contents"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    title = Column(String(1024), nullable=True)
    caption = Column(Text(), nullable=True)
    blocks = Column(ARRAY(JSON), nullable=True)
    slug = Column(String(300))
    is_published = Column(Boolean(), default=False)
    cover_image = Column(String(1024))
    time = Column(String(200), nullable=True)
    version = Column(String(200), nullable=True)

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value, allow_unicode=True)

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

    content_categories = relationship(
        "ContentCategory",
        back_populates="content",
        cascade="all,delete"
    )
    content_labels = relationship(
        "ContentLabel",
        back_populates="content",
        cascade="all,delete"
    )
    user = relationship(
        "User", back_populates="content")


event.listen(Content.title, 'set', Content.generate_slug, retval=False)
