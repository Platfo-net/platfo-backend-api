from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CampaignLead(Base):
    __tablename__ = 'notifier_campaign_leads'

    lead_igs_id = Column(BigInteger, nullable=True)

    is_sent = Column(Boolean(), default=False)
    is_seen = Column(Boolean(), default=False)
    mid = Column(String(255), nullable=True)

    reaction = Column(String(100), nullable=True)

    lead_id = Column(
        BigInteger,
        ForeignKey('live_chat_leads.id'),
        nullable=True,
    )
    campaign_id = Column(
        BigInteger, ForeignKey('notifier_campaigns.id'), nullable=True, index=True
    )
    campaign = relationship('Campaign', back_populates='campaign_leads')
    lead = relationship('Lead', back_populates='campaign_leads')
