from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TelegramLeadMessage(Base):
    __tablename__ = 'social_telegram_lead_messages'
    lead_id = Column(
        BigInteger,
        ForeignKey('social_telegram_leads.id'),
        nullable=True,
    )
    is_lead_to_bot = Column(
        Boolean,
        nullable=True,
    )
    message = Column(Text, nullable=True)
    message_id = Column(BigInteger, nullable=True, index=True)
    mirror_message_id = Column(BigInteger, nullable=True, index=True)
    reply_to_id = Column(BigInteger, nullable=True, index=True)

    lead = relationship('TelegramLead', back_populates='messages')
