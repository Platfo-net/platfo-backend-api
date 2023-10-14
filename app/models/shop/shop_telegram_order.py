import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopTelegramOrder(Base):
    __tablename__ = 'shop_telegram_orders'
    message_reply_to_id = Column(Integer(), nullable=True)
    support_bot_message_id = Column(Integer(), nullable=True)
    bot_message_id = Column(Integer(), nullable=True)
    message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    order_id = Column(
        BigInteger,
        ForeignKey('shop_orders.id'),
        nullable=True,
    )

    order = relationship('ShopOrder', back_populates='telegram_order')
