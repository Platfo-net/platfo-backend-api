from sqlalchemy import BigInteger, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopOrderItem(Base):
    __tablename__ = 'shop_order_items'

    order_id = Column(
        BigInteger,
        ForeignKey('shop_orders.id'),
        nullable=True,
    )

    product_id = Column(
        BigInteger,
        ForeignKey('shop_products.id'),
        nullable=True,
    )

    count = Column(Integer, default=1)

    order = relationship('ShopOrder', back_populates='items')
    product = relationship('ShopProduct', back_populates='order_items')
