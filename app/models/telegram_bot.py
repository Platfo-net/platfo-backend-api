from sqlalchemy import BigInteger, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TelegramBot(Base):
    __tablename__ = 'telegram_bots'

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        primary_key=False,
        nullable=True,
    )

    bot_token = Column(String(255), nullable=True)

    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    bot_id = Column(BigInteger, nullable=True, index=True)
    welcome_message = Column(Text(), nullable=True)

    user = relationship('User', back_populates='telegram_bots')

    telegram_bot_shop = relationship("ShopShopTelegramBot", back_populates="telegram_bot")
    leads = relationship("TelegramLead", back_populates="telegram_bot")
