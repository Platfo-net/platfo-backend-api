
import datetime

from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, \
    String, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.constants.campaign_status import CampaignStatus


class Campaign(Base):

    __tablename__ = "postman_campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    is_draft = Column(Boolean(), default=True)

    facebook_page_id = Column(String(100), nullable=True)
    status = Column(String(255), nullable=True, default=CampaignStatus.PENDING)
    is_active = Column(Boolean(), default=False)

    content = Column(JSON, nullable=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="campaign")
    campaign_contacts = relationship(
        "CampaignContact", back_populates="campaign"
    )
