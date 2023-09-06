from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TelegramLead(Base):
    __tablename__ = 'lead_telegram_leads'

    chat_id = Column(BigInteger, nullable=True, index=True)
    telegram_bot_id = Column(
        BigInteger,
        ForeignKey('telegram_bots.id'),
        nullable=True,
    )

    telegram_bot = relationship('TelegramBot', back_populates='leads')
