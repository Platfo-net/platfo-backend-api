
from uuid import uuid4

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Label(Base):
    __tablename__ = "labels"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    label_name = Column(String(255), nullable=True)

    content_labels = relationship(
        "ContentLabel", back_populates="label")
