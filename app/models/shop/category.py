from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopCategory(Base):
    __tablename__ = 'shop_categories'

    title = Column(String(255), nullable=True)

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )

    user = relationship('User', back_populates='shop_categories')
    products = relationship('ShopProduct', back_populates='category')
