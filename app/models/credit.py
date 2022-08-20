import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Credit(Base):

    __tablename__ = "credits"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=False,
        nullable=True,
    )

    to_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    user = relationship(
        "User", back_populates="credit")
