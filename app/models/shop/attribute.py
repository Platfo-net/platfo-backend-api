from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopAttribute(Base):
    __tablename__ = 'shop_attributes'

    key = Column(String(255), nullable=True)
    value = Column(String(255), nullable=True)

    product_id = Column(
        BigInteger,
        ForeignKey('shop_products.id', ondelete="SET NULL"),
        nullable=True,
    )

    product = relationship('ShopProduct', back_populates='attributes')
