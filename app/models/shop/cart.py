from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopCart(Base):
    __tablename__ = 'shop_carts'

    
    
    cart_items = relationship("ShopCart" , back_populates="cart")