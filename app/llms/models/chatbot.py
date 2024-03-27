from sqlalchemy import Column, String, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.llms.models.base import Base


class ChatBot(Base):
    __tablename__ = 'chatbots'

    name = Column(String(255))
    description = Column(Text(), nullable=True)
    prompt = Column(Text(), nullable=True)
    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )
    user = relationship('User', back_populates='user_chatbots')
    knowledge_bases = relationship("KnowledgeBase", backref="chatbot")
