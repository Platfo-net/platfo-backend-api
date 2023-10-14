from sqlalchemy import (BigInteger, Column, DateTime, ForeignKey, Integer,
                        String)
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

    # payment information
    payment_reference_number = Column(String(255), nullable=True)
    payment_card_last_four_number = Column(String(16), nullable=True)
    payment_datetime = Column(DateTime, nullable=True)
    payment_receipt_image = Column(String(255), nullable=True)
    # -----

    order_number = Column(Integer, nullable=True, index=True)
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

    payment_method_id = Column(
        BigInteger,
        ForeignKey('shop_payment_methods.id'),
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates='orders')

    items = relationship("ShopOrderItem", back_populates="order")
    lead = relationship("TelegramLead", back_populates="orders")

    payment_method = relationship("ShopPaymentMethod", back_populates="orders")
    shipment_method = relationship("ShopShipmentMethod", back_populates="orders")
    telegram_order = relationship("ShopTelegramOrder", back_populates="order")
