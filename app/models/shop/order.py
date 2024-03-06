import datetime

from sqlalchemy import (JSON, BigInteger, Boolean, Column, DateTime, Float,
                        ForeignKey, Integer, String)

from sqlalchemy.orm import relationship

from app.constants.order_status import OrderStatus
from app.db.base_class import Base


class ShopOrder(Base):
    __tablename__ = 'shop_orders'

    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone_number = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    postal_code = Column(String(255), nullable=True)
    status = Column(String(255), default=OrderStatus.UNPAID["value"])

    order_number = Column(Integer, nullable=True, index=True)
    total_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    payment_information = Column(JSON, nullable=True)

    lead_id = Column(
        BigInteger,
        ForeignKey('social_telegram_leads.id'),
        nullable=True,
    )

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    shipment_method_id = Column(
        BigInteger,
        ForeignKey('shop_shipment_methods.id'),
        nullable=True,
    )

    table_id = Column(
        BigInteger,
        ForeignKey('shop_tables.id'),
        nullable=True,
    )

    shop_payment_method_id = Column(
        BigInteger,
        ForeignKey('shop_shop_payment_methods.id'),
        nullable=True,
    )

    shipment_cost_currency = Column(String(32), nullable=True)
    shipment_cost_amount = Column(Float, nullable=True)

    payment_information = Column(JSON, nullable=True)
    payment_image = Column(String(255), nullable=True)

    shop = relationship('ShopShop', back_populates='orders')

    items = relationship("ShopOrderItem", back_populates="order")
    lead = relationship("TelegramLead", back_populates="orders")

    shop_payment_method = relationship("ShopShopPaymentMethod", back_populates="orders")
    shipment_method = relationship("ShopShipmentMethod", back_populates="orders")
    telegram_order = relationship("ShopTelegramOrder", back_populates="order")
    table = relationship("ShopTable", back_populates="orders")
