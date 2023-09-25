from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopCategory(Base):
    __tablename__ = 'shop_categories'

    title = Column(String(255), nullable=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    products = relationship('ShopProduct', back_populates='category')

    shop = relationship('ShopShop', back_populates='categories')