import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, Float,
                        ForeignKey, String)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopProduct(Base):
    __tablename__ = 'shop_products'

    title = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    price = Column(Float(), nullable=True)
    currency = Column(String(32), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    category_id = Column(
        BigInteger,
        ForeignKey('shop_categories.id', ondelete="SET NULL"),
        nullable=True,
    )

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id', ondelete="CASCADE"),
        nullable=True,
    )

    is_active = Column(Boolean(), default=True)
    is_available = Column(Boolean(), default=True)

    category = relationship('ShopCategory', back_populates='products')
    order_items = relationship('ShopOrderItem', back_populates="product")

    shop = relationship('ShopShop', back_populates="products")
