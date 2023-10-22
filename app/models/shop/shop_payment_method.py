from sqlalchemy import JSON, BigInteger, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopShopPaymentMethod(Base):
    __tablename__ = 'shop_shop_payment_methods'

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id', ondelete="CASCADE"),
        nullable=True,
    )

    payment_method_id = Column(
        BigInteger,
        ForeignKey('shop_payment_methods.id', ondelete="CASCADE"),
        nullable=True,
    )

    information = Column(JSON, nullable=True)

    is_active = Column(Boolean(), default=False)

    shop = relationship('ShopShop', back_populates="payment_methods")
    payment_method = relationship('ShopPaymentMethod', back_populates="shops")
