import datetime
from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, DateTime, JSON, Boolean, BigInteger
from sqlalchemy.orm import relationship
from app.constants.campaign_status import CampaignStatus


class Campaign(Base):
    __tablename__ = "postman_campaigns"

    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    group_name = Column(String(255), nullable=True)

    is_draft = Column(Boolean(), default=True)

    facebook_page_id = Column(BigInteger, nullable=True, index=True)
    status = Column(String(255), nullable=True, default=CampaignStatus.PENDING)
    is_active = Column(Boolean(), default=False)

    content = Column(JSON, nullable=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="campaign")
    campaign_contacts = relationship("CampaignContact", back_populates="campaign")
