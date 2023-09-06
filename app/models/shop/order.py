from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
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
    status = Column(String(255), default=OrderStatus.UNPAID)

    order_number = Column(Integer, nullable=True, index=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates='orders')

    items = relationship("ShopOrderItem", back_populates="order")
