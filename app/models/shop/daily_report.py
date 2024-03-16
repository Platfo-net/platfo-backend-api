from sqlalchemy import BigInteger, Column, Date, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopDailyReport(Base):
    __tablename__ = 'shop_daily_reports'

    order_count = Column(Float, nullable=True)
    order_amount = Column(Float, nullable=True)
    date = Column(Date, nullable=True)

    shop_id = Column(
        BigInteger,
        ForeignKey('shop_shops.id', ondelete="CASCADE"),
        nullable=True,
    )

    shop = relationship('ShopShop', back_populates='daily_reports')
