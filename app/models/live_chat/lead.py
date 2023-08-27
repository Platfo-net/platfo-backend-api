import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, String)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Lead(Base):
    __tablename__ = 'live_chat_leads'

    lead_igs_id = Column(BigInteger, nullable=True, index=True)
    facebook_page_id = Column(BigInteger, nullable=True, index=True)

    last_message = Column(String(1024), nullable=True)
    last_message_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_interaction_at = Column(DateTime, default=datetime.datetime.utcnow)

    username = Column(String(255), nullable=True)
    profile_image = Column(String(1024), nullable=True)
    name = Column(String(128), nullable=True)
    followers_count = Column(Integer, nullable=True)
    is_verified_user = Column(Boolean, nullable=True)
    is_user_follow_business = Column(Boolean, nullable=True)
    is_business_follow_user = Column(Boolean, nullable=True)

    first_impression = Column(String(100), nullable=True)

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )

    user = relationship('User', back_populates='leads')

    campaign_leads = relationship(
        'CampaignLead', back_populates='lead', cascade='all,delete'
    )