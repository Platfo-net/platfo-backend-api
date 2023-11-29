from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base_class import Base


class ShopCategory(Base):
    __tablename__ = 'shop_categories'

    title = Column(String(255), nullable=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    image = Column(String(255), nullable=True)

    is_active = Column(Boolean(), default=True)

    is_deleted = Column(Boolean(), nullable=False, default=False,
                        server_default=expression.false())

    products = relationship('ShopProduct', back_populates='category')

    shop = relationship('ShopShop', back_populates='categories')
