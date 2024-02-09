from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopTable(Base):
    __tablename__ = 'shop_tables'

    title = Column(String(255), nullable=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates='tables')
    orders = relationship('ShopOrder', back_populates='table')
