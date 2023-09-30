from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class ShopCredit(Base):
    __tablename__ = 'credit_shop_credits'

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id'),
        primary_key=False,
        nullable=False,
        index=True,
        unique=True,
    )
    expires_at = Column(DateTime(), nullable=True, default=datetime.now)

    shop = relationship('ShopShop', back_populates='credit')
