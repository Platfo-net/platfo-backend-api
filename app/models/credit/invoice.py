import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, Float,
                        ForeignKey, Integer, String)
from sqlalchemy.orm import relationship

from app.constants.currency import Currency
from app.constants.payment_status import PaymentStatus
from app.db.base_class import Base


class Invoice(Base):
    __tablename__ = 'credit_invoices'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    payed_at = Column(DateTime, nullable=True)

    amount = Column(Float(), nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default=Currency.IRT)
    bought_on_discount = Column(Boolean(), default=False)

    plan_name = Column(String(255), nullable=True)
    module = Column(String(255), nullable=True)
    extend_days = Column(Integer(), nullable=True)
    extend_count = Column(Integer(), nullable=True)

    status = Column(String(10), default=PaymentStatus.PENDING['name'])

    # TODO : data from ipg

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        primary_key=False,
        nullable=False,
    )

    user = relationship('User', back_populates='invoices')
