from sqlalchemy import BigInteger, Column, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TelegramLeadMessage(Base):
    __tablename__ = 'social_telegram_lead_messages'
    lead_id = Column(
        BigInteger,
        ForeignKey('telegram_bots.id'),
        nullable=True,
    )
    is_lead_to_bot = Column(
        Boolean,
        nullable=True,
    )
    message = Column(Text, nullable=True)
    message_id = Column(BigInteger, nullable=True, index=True)
    mirror_message_id = Column(BigInteger, nullable=True, index=True)

    lead = relationship('TelegramBot', back_populates='messages')
