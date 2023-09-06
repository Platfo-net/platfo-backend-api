from sqlalchemy import BigInteger, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopShop(Base):
    __tablename__ = 'shop_shops'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)
    category = Column(String(255), nullable=True)

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )

    user = relationship('User', back_populates='shops')

    products = relationship('ShopProduct', back_populates='shop')
    categories = relationship('ShopCategory', back_populates='shop')
    orders = relationship("ShopOrder", back_populates="shop")

    shop_telegram_bot = relationship("ShopShopTelegramBot", back_populates="shop")
