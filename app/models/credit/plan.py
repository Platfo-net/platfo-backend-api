import datetime
from app.constants.currency import Currency
from app.constants.module import Module
from app.db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Float, \
    String, Text, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import relationship


class Plan(Base):

    __tablename__ = "credit_plans"

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    is_active = Column(Boolean(), default=True)

    extend_days = Column(Integer(), nullable=True)
    extend_count = Column(Integer(), nullable=True)

    original_price = Column(Float(), nullable=False, default=0.0)
    discounted_price = Column(Float(), nullable=False, default=0.0)

    discount_percentage = Column(Float(), nullable=False, default=0.0)
    is_discounted = Column(Float(), nullable=False, default=0.0)

    currency = Column(String(10), nullable=False, default=Currency.IRR)

    module = Column(String(255), nullable=False, default=Module.NOTIFIER)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    features = relationship("PlanFeature", back_populates="plan")
    invoices = relationship("Invoice", back_populates="plan")
    credit_logs = relationship("CreditLog", back_populates="plan")


class PlanFeature(Base):
    __tablename__ = "credit_plan_features"

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    plan_id = Column(
        BigInteger,
        ForeignKey("credit_plans.id"),
        primary_key=False,
        nullable=False,
    )
    plan = relationship("Plan", back_populates="features")
