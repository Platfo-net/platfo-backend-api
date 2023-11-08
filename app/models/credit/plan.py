import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import relationship

from app.constants.currency import Currency
from app.constants.module import Module
from app.db.base_class import Base


class Plan(Base):
    __tablename__ = 'credit_plans'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    is_active = Column(Boolean(), default=True)

    extend_days = Column(Integer(), nullable=True)
    extend_count = Column(Integer(), nullable=True)

    original_price = Column(Float(), nullable=False, default=0.0)
    discounted_price = Column(Float(), nullable=False, default=0.0)

    discount_percentage = Column(Float(), nullable=False, default=0.0)

    currency = Column(String(10), nullable=False, default=Currency.IRT["value"])

    module = Column(String(255), nullable=False, default=Module.TELEGRAM_SHOP)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    features = relationship('PlanFeature', back_populates='plan')
    shop_telegram_payment_records = relationship(
        'CreditShopTelegramPaymentRecord', back_populates='plan')


class PlanFeature(Base):
    __tablename__ = 'credit_plan_features'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    plan_id = Column(
        BigInteger,
        ForeignKey('credit_plans.id'),
        primary_key=False,
        nullable=False,
    )
    plan = relationship('Plan', back_populates='features')
