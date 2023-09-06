import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        String)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopShopTelegramBot(Base):
    __tablename__ = 'shop_shop_telegram_bots'

    support_token = Column(String(255), nullable=True)
    support_bot_token = Column(String(255), nullable=True)
    support_account_chat_id = Column(BigInteger, index=True, nullable=True)
    is_support_verified = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    telegram_bot_id = Column(
        BigInteger,
        ForeignKey('telegram_bots.id'),
        nullable=True,
    )

    shop = relationship("ShopShop", back_populates="shop_telegram_bot")
    telegram_bot = relationship("TelegramBot", back_populates="telegram_bot_shop")
