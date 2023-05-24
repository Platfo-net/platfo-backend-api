from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class GroupContact(Base):
    __tablename__ = "notifier_group_contacts"

    contact_igs_id = Column(BigInteger, nullable=True)

    contact_id = Column(
        BigInteger,
        ForeignKey("live_chat_contacts.id"),
        nullable=True,
    )

    group_id = Column(
        BigInteger,
        ForeignKey("notifier_groups.id"),
        nullable=True,
        index=True,
    )
    group = relationship("Group", back_populates="group_contacts")
    contact = relationship("Contact", back_populates="group_contacts")
