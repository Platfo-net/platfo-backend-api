from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TelegramLead(Base):
    __tablename__ = 'social_telegram_leads'
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    chat_id = Column(BigInteger, nullable=True, index=True)
    telegram_bot_id = Column(
        BigInteger,
        ForeignKey('telegram_bots.id'),
        nullable=True,
    )

    telegram_bot = relationship('TelegramBot', back_populates='leads')
    orders = relationship('ShopOrder', back_populates='lead')
    messages = relationship('TelegramLeadMessage', back_populates='lead')
