import datetime
from app.constants.currency import Currency
from app.db.base_class import Base
from sqlalchemy import Column, DateTime, String, ForeignKey, BigInteger, Float
from sqlalchemy.orm import relationship
from app.constants.payment_status import PaymentStatus


class Invoice(Base):

    __tablename__ = "plans"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    payed_at = Column(DateTime, nullable=True)

    amount = Column(Float(), nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default=Currency.IRR)

    status = Column(String(10), default=PaymentStatus.PENDING["name"])

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        primary_key=False,
        nullable=False,
    )

    plan_id = Column(
        BigInteger,
        ForeignKey("plans.id"),
        primary_key=False,
        nullable=False,
    )

    user = relationship("User", back_populates="invoices")
    plan = relationship("Plan", back_populates="invoices")
    credit_logs = relationship("CreditLog", back_populates="invoices")
