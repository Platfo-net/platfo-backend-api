from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, \
    Text
from sqlalchemy.orm import relationship

from app.constants.currency import Currency
from app.db.base_class import Base
from app.llms.models import WithDates


class ChatBotPlan(Base, WithDates):
    __tablename__ = 'chatbot_plans'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    is_active = Column(Boolean(), default=True)
    is_extra = Column(Boolean(), default=True)

    extend_days = Column(Integer(), nullable=True)
    extend_chat_count = Column(Integer(), nullable=True)
    extend_token_count = Column(Integer(), nullable=True)

    price = Column(Float(), nullable=False, default=0.0)

    currency = Column(String(10), nullable=False, default=Currency.IRT["value"])

    features = relationship('ChatbotPlanFeature', back_populates='chatbot_plan')


class ChatBotPlanFeature(Base):
    __tablename__ = 'chatbot_plan_features'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    chatbot_plan_id = Column(
        BigInteger,
        ForeignKey('chatbot_plans.id'),
        primary_key=False,
        nullable=False,
    )
    chatbot_plan = relationship('ChatBotPlan', back_populates='features')


class PurchasedChatBotPlan(Base):
    __tablename__ = 'purchased_chatbot_plans'

    from_datetime = Column(DateTime)
    to_datetime = Column(DateTime)
    is_extra = Column(Boolean, default=False)
    remaining_chat_count = Column(BigInteger, default=0)
    remaining_token_count = Column(BigInteger, default=0)

    chatbot_id = Column(
        BigInteger,
        ForeignKey('chatbots.id', ondelete="CASCADE"),
        primary_key=False,
        nullable=False,
    )


class ChatBotTransaction(Base, WithDates):
    __tablename__ = 'chatbot_transaction'
    title = Column(String(255), nullable=True)
    payed_at = Column(DateTime, nullable=True)
    is_paid = Column(Boolean, default=False)
    is_extra = Column(Boolean, default=False)

    extend_days = Column(Integer(), nullable=True)
    extend_chat_count = Column(Integer(), nullable=True)
    extend_token_count = Column(Integer(), nullable=True)

    amount = Column(Float(), nullable=False, default=0.0)
    payment_authority = Column(String(255), nullable=True)

    currency = Column(String(10), nullable=False, default=Currency.IRT["value"])

    chatbot_id = Column(
        BigInteger,
        ForeignKey('chatbots.id', ondelete="CASCADE"),
        primary_key=False,
        nullable=False,
    )
