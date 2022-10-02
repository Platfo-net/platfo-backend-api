
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ContentLabel(Base):
    __tablename__ = "content_labels"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    content_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contents.id"),
        nullable=True,
    )
    label_id = Column(
        UUID(as_uuid=True),
        ForeignKey("labels.id"),
        nullable=True,
    )
    label = relationship("Label", back_populates="content_labels")
    content = relationship("Content", back_populates="content_labels")
