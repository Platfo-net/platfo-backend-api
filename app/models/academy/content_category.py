from uuid import uuid4


from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ContentCategory(Base):
    __tablename__ = "content_categories"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    content_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contents.id"),
        nullable=True,
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
    )

    category = relationship("Category", back_populates="content_categories")
    content = relationship("Content", back_populates="content_categories")
