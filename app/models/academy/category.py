from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Category(Base):

    __tablename__ = "academy_categories"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    title = Column(String(255), nullable=True)
    parrent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("academy_categories.id"),
        nullable=True,
    )

    content_categories = relationship(
        "ContentCategory", back_populates="category")
