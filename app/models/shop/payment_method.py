from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopPaymentMethod(Base):
    __tablename__ = 'shop_payment_methods'

    title = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    information_fields = Column(JSON(), nullable=True)
    payment_fields = Column(JSON, nullable=True)

    shops = relationship('ShopShopPaymentMethod', back_populates="payment_method")
    orders = relationship('ShopOrder', back_populates="payment_method")
