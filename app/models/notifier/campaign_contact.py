from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, Boolean, BigInteger
from sqlalchemy.orm import relationship


class CampaignContact(Base):
    __tablename__ = "notifier_campaign_contacts"

    contact_igs_id = Column(BigInteger, nullable=True)

    is_sent = Column(Boolean(), default=False)
    is_seen = Column(Boolean(), default=False)
    mid = Column(String(255), nullable=True)

    reaction = Column(String(100), nullable=True)

    contact_id = Column(
        BigInteger,
        ForeignKey("live_chat_contacts.id"),
        nullable=True,
    )
    campaign_id = Column(
        BigInteger,
        ForeignKey("notifier_campaigns.id"),
        nullable=True,
        index=True
    )
    campaign = relationship("Campaign", back_populates="campaign_contacts")
    contact = relationship("Contact", back_populates="campaign_contacts")
