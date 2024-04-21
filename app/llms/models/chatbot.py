from sqlalchemy import BigInteger, Column, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.llms.models.base import WithDates
from app.llms.utils import config


class ChatBot(Base, WithDates):
    __tablename__ = 'chatbots'

    name = Column(String(255))
    description = Column(Text(), nullable=True)
    prompt = Column(Text(), nullable=True, default=config.DEFAULT_PROMPT)
    temperature = Column(
        Float,
        nullable=True,
        default=0,
    )
    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )
    user = relationship('User', back_populates='chatbots')
    knowledge_bases = relationship("KnowledgeBase", back_populates="chatbot")
