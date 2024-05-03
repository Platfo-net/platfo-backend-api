from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChatBotTelegramBot(Base):
    __tablename__ = 'chatbot_telegram_bots'

    chatbot_id = Column(
        BigInteger,
        ForeignKey('chatbots.id', ondelete="CASCADE"),
        nullable=True,
    )

    telegram_bot_id = Column(
        BigInteger,
        ForeignKey('telegram_bots.id', ondelete="CASCADE"),
        nullable=True,
    )

    telegram_bot = relationship("TelegramBot", back_populates="chatbot_telegram_bot")
    chatbot = relationship("ChatBot", back_populates="chatbot_telegram_bot")
