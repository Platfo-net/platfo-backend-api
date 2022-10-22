
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Campaign(Base):

    __tablename__ = "postman_campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    page_id = Column(String(100), nullable=True)
    status = Column(String(255), nullable=True, default='PENDING')

    contact_count = Column(Integer(), nullable=True, default=0)
    sent_count = Column(Integer(), nullable=True, default=0)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    user = relationship("User", back_populates="campaign")
    campaign_contacts = relationship(
        "CampaignContact", back_populates="campaign", cascade="all,delete"
    )
