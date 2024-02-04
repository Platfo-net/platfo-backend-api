from sqlalchemy import BigInteger, Column, Boolean, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShopProductVariant(Base):
    __tablename__ = 'shop_product_variants'

    product_id = Column(
        BigInteger,
        ForeignKey('shop_products.id', ondelete="SET NULL"),
        nullable=True,
    )

    price = Column(Float(), nullable=True)
    currency = Column(String(32), nullable=True)
    title = Column(String(256), nullable=True)
    is_available = Column(Boolean(256), nullable=True, default=True)

    product = relationship('ShopProduct', back_populates='variants')
