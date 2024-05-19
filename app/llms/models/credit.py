from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, String

from app.constants.currency import Currency
from app.db.base_class import Base
from app.llms.models import WithDates


class UserChatBotCredit(Base):
    __tablename__ = 'chatbot_credits'

    amount = Column(Float(), nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default=Currency.IRT["value"])

    user_id = Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"), primary_key=False,
                     nullable=True, index=True)


class ChatBotTransaction(Base, WithDates):
    __tablename__ = 'chatbot_transaction'
    payed_at = Column(DateTime, nullable=True)  # TODO fix this please
    is_paid = Column(Boolean, default=False)

    amount = Column(Float(), nullable=False, default=0.0)
    payment_authority = Column(String(255), nullable=True)

    currency = Column(String(10), nullable=False, default=Currency.IRT["value"])

    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete="CASCADE"),
        primary_key=False,
        nullable=True,
    )
