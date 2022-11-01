
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Group(Base):
    __tablename__ = "postman_groups"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    facebook_page_id = Column(String(255), nullable=True)

    user = relationship("User", back_populates="group")
    group_contact = relationship("GroupContact", back_populates="group")
