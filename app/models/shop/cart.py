from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopCart(Base):
    __tablename__ = 'shop_carts'

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates='carts')

    cart_items = relationship("ShopCartItem", back_populates="cart")
