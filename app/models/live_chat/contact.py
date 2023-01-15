import datetime
from uuid import uuid4

from sqlalchemy.orm import relationship

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, JSON, DateTime, Integer , BigInteger
from sqlalchemy.dialects.postgresql import UUID


class Contact(Base):

    __tablename__ = "live_chat_contacts"

    contact_igs_id = Column(BigInteger, nullable=True , index = True)
    user_page_id = Column(BigInteger, nullable=True , index=True)

    last_message = Column(String(1024), nullable=True)
    last_message_at = Column(DateTime, default=datetime.datetime.utcnow)

    information = Column(JSON, nullable=True)

    message_count = Column(Integer(), nullable=True, default=0)
    comment_count = Column(Integer(), nullable=True, default=0)
    live_comment_count = Column(Integer(), nullable=True, default=0)
    first_impression = Column(String(100), nullable=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
    )
    campaign_contacts = relationship(
        "CampaignContact", back_populates="contact", cascade="all,delete"
    )

    group_contact = relationship(
        "GroupContact", back_populates="contact", cascade="all,delete"
    )
