from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Text
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
    is_info_required = Column(Boolean(), default=False)

    user = relationship('User', back_populates='shops')

    orders = relationship("ShopOrder", back_populates="shop")

    shop_telegram_bot = relationship("ShopShopTelegramBot", back_populates="shop")
    categories = relationship("ShopCategory", back_populates="shop")
    products = relationship("ShopProduct", back_populates="shop")
    payment_methods = relationship("ShopPaymentMethod", back_populates="shop")
    shipment_methods = relationship("ShopShipmentMethod", back_populates="shop")
    credit = relationship("ShopCredit", back_populates="shop")
    payment_methods = relationship("ShopShopPaymentMethod", back_populates="shop")
    payment_records = relationship("CreditShopTelegramPaymentRecord", back_populates="shop")
    tables = relationship("ShopTable", back_populates="shop")
    theme = relationship('ShopTheme', back_populates='shop')
