from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChatBotTelegramBot(Base):
    __tablename__ = 'chatbot_telegram_bots'

    chatbot_id = Column(
        BigInteger,
        ForeignKey('chatbots.id', ondelete="CASCADE"),
        nullable=False,
    )

    telegram_bot_id = Column(
        BigInteger,
        ForeignKey('telegram_bots.id', ondelete="CASCADE"),
        nullable=False,
    )

    telegram_bot = relationship("TelegramBot", cascade="delete",
                                back_populates="chatbot_telegram_bot")
    chatbot = relationship("ChatBot", cascade="delete", back_populates="chatbot_telegram_bot")
