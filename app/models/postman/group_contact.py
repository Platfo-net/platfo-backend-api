
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class GroupContact(Base):
    __tablename__ = "postman_group_contacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    contact_igs_id = Column(String(100), nullable=True)

    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("live_chat_contacts.id"),
        nullable=True,
    )

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("postman_groups.id"),
        nullable=True,
    )
    group = relationship("Group", back_populates="group_contact")
    contact = relationship("Contact", back_populates="group_contact")
