import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, String
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
        ForeignKey('shop_categories.id'),
        nullable=True,
    )

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )

    user = relationship('User', back_populates='shop_products')
    category = relationship('ShopCategory', back_populates='products')
