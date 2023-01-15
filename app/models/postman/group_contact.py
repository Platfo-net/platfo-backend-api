from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class GroupContact(Base):
    __tablename__ = "postman_group_contacts"

    contact_igs_id = Column(BigInteger, nullable=True)

    contact_id = Column(
        BigInteger,
        ForeignKey("live_chat_contacts.id"),
        nullable=True,
    )

    group_id = Column(
        BigInteger,
        ForeignKey("postman_groups.id"),
        nullable=True,
        index=True,
    )
    group = relationship("Group", back_populates="group_contact")
    contact = relationship("Contact", back_populates="group_contact")
