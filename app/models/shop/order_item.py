from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String
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
        ForeignKey('shop_products.id', ondelete="SET NULL"),
        nullable=True,
    )

    variant_title = Column(String(255), nullable=True)
    product_title = Column(String(255), nullable=True)

    count = Column(Integer, default=1)
    price = Column(Float(), nullable=True)
    currency = Column(String(32), nullable=True)

    order = relationship('ShopOrder', back_populates='items')
    product = relationship('ShopProduct', back_populates='order_items')
    variant = relationship('ShopProductVariant', back_populates='order_items')
