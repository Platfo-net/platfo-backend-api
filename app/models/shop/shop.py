import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopShop(Base):
    __tablename__ = 'shop_shops'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)
    category = Column(String(255), nullable=True)

    support_token = Column(String(255), nullable=True)
    support_bot_token = Column(String(255) , nullable=True)
    support_account_chat_id = Column(BigInteger, index=True, nullable=True)
    is_support_verified = Column(Boolean() , default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )

    user = relationship('User', back_populates='shops')

    products = relationship('ShopProduct', back_populates='shop')
    categories = relationship('ShopCategory', back_populates='shop')
    carts = relationship("ShopCart" , back_populates="shop")
