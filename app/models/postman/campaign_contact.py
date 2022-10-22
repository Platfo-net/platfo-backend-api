
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class CampaignContact(Base):
    __tablename__ = "postman_campaign_contacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    contact_igsid = Column(String(100), nullable=True)
    is_seen = Column(Boolean(), default=True)
    reaction = Column(String(100), nullable=True)

    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("live_chat_contacts.id"),
        nullable=True,
    )
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("postman_campaigns.id"),
        nullable=True,
    )
    campaign = relationship("Campaign", back_populates="campaign_contacts")
    contact = relationship("Contact", back_populates="campaign_contacts")
