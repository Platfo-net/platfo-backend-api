from sqlalchemy import Column, String, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.llms.models.base import WithDates


class ChatBot(Base, WithDates):
    __tablename__ = 'chatbots'

    name = Column(String(255))
    description = Column(Text(), nullable=True)
    prompt = Column(Text(), nullable=True)
    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )
    user = relationship('User', back_populates='chatbots')
    knowledge_bases = relationship("KnowledgeBase", back_populates="chatbot")
