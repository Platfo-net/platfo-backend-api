import datetime
from uuid import uuid4

from sqlalchemy.orm import relationship

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, JSON, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID


class Contact(Base):

    __tablename__ = "live_chat_contacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    contact_igs_id = Column(String(64), nullable=True)
    user_page_id = Column(String(64), nullable=True)

    last_message = Column(JSON, nullable=True)
    last_message_at = Column(DateTime, default=datetime.datetime.utcnow)

    information = Column(JSON, nullable=True)

    message_count = Column(Integer(), nullable=True, default=0)
    comment_count = Column(Integer(), nullable=True, default=0)
    live_comment_count = Column(Integer(), nullable=True, default=0)
    first_impression = Column(String(100), nullable=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    campaign_contacts = relationship(
        "CampaignContact", back_populates="contact", cascade="all,delete"
    )

    group_contacts = relationship(
        "GroupContact", back_populates="contact", cascade="all,delete"
    )
