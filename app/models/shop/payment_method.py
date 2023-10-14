from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopPaymentMethod(Base):
    __tablename__ = 'shop_payment_methods'

    title = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates="payment_methods")
    orders = relationship('ShopOrder', back_populates="payment_method")
