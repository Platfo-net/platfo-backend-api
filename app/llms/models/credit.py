import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, \
    Text
from sqlalchemy.orm import relationship

from app.constants.currency import Currency
from app.db.base_class import Base


class ChatbotPlan(Base):
    __tablename__ = 'chatbot_plans'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    is_active = Column(Boolean(), default=True)
    is_extra = Column(Boolean(), default=True)

    extend_days = Column(Integer(), nullable=True)
    extend_chat_count = Column(Integer(), nullable=True)
    extend_token_count = Column(Integer(), nullable=True)

    original_price = Column(Float(), nullable=False, default=0.0)

    currency = Column(String(10), nullable=False, default=Currency.IRT["value"])

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    features = relationship('ChatbotPlanFeature', back_populates='plan')


class ChatbotPlanFeature(Base):
    __tablename__ = 'chatbot_plan_features'

    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)

    plan_id = Column(
        BigInteger,
        ForeignKey('chatbot_plans.id'),
        primary_key=False,
        nullable=False,
    )
    plan = relationship('Plan', back_populates='features')


class PurchasedChatbotPlan(Base):
    __tablename__ = 'purchased_chatbot_plans'

    from_datetime = Column(DateTime)
    to_datetime = Column(DateTime)
    is_extra = Column(Boolean, default=False)
    remaining_chat_count = Column(BigInteger, default=0)
    remaining_token_count = Column(BigInteger, default=0)

    chatbot_id = Column(
        BigInteger,
        ForeignKey('chatbots.id'),
        primary_key=False,
        nullable=False,
    )
