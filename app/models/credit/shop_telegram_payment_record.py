import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.constants.shop_telegram_payment_status import \
    ShopTelegramPaymentRecordStatus
from app.db.base_class import Base


class CreditShopTelegramPaymentRecord(Base):
    __tablename__ = 'credit_shop_telegram_payment_records'

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        primary_key=False,
        nullable=True,
    )

    plan_id = Column(
        BigInteger,
        ForeignKey('credit_plans.id'),
        primary_key=False,
        nullable=True,
    )

    reply_to_message_id = Column(BigInteger, nullable=True)
    image = Column(String(255), nullable=True)
    payment_message_id = Column(BigInteger, nullable=True)

    status = Column(String(32), default=ShopTelegramPaymentRecordStatus.CREATED)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    shop = relationship('ShopShop', back_populates='payment_records')
    plan = relationship('Plan', back_populates='shop_telegram_payment_records')
