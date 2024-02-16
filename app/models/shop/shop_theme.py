from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopTheme(Base):
    __tablename__ = 'shop_themes'

    color_code = Column(String(255), nullable=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        unique=True,
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates='theme')
