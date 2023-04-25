from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import relationship


class CreditLog(Base):

    __tablename__ = "credit_credit_logs"

    module = Column(String(20), nullable=False)
    count = Column(Integer(), nullable=True)
    days_added = Column(Integer(), nullable=True)

    plan_id = Column(
        BigInteger,
        ForeignKey("credit_plans.id"),
        primary_key=False,
        nullable=False,
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        primary_key=False,
        nullable=False,
    )
    invoice_id = Column(
        BigInteger,
        ForeignKey("credit_invoices.id"),
        primary_key=False,
        nullable=False,
    )

    user = relationship("User", back_populates="credit_logs")
    plan = relationship("Plan", back_populates="credit_logs")
    invoice = relationship("Invoice", back_populates="credit_logs")
