from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopCartItem(Base):
    __tablename__ = 'shop_cart_items'


    cart_id = Column(
        BigInteger,
        ForeignKey('shop_carts.id'),
        nullable=True,
    )
    
    product_id = Column(
        BigInteger,
        ForeignKey('shop_products.id'),
        nullable=True,
    )

    cart = relationship('ShopCart', back_populates='cart_items')
    product = relationship('ShopProduct', back_populates='cart_items')
