from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Category(Base):
    __tablename__ = 'academy_categories'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    title = Column(String(255), nullable=True)
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey('academy_categories.id'),
        nullable=True,
    )

    content_categories = relationship('ContentCategory', back_populates='category')

    parent_categories = relationship('Category', cascade='all,delete')
