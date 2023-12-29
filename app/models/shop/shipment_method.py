from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String , Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopShipmentMethod(Base):
    __tablename__ = 'shop_shipment_methods'

    title = Column(String(255), nullable=True)
    price = Column(Float(), nullable=True)
    currency = Column(String(255), nullable=True)

    is_active = Column(Boolean(), default=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates="shipment_methods")

    orders = relationship('ShopOrder', back_populates="shipment_method")
