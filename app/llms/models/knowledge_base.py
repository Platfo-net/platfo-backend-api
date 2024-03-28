import enum

from sqlalchemy import Column, ForeignKey, String, BigInteger, JSON, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.llms.models.base import WithDates


class KnowledgeBase(Base, WithDates):
    __tablename__ = 'knowledgebase'

    name = Column(String(255), nullable=False)
    metadatas = Column(JSON(), nullable=True)
    type = Column(String(40), nullable=True)
    file_path = Column(String(255), nullable=True)
    chatbot_id = Column(BigInteger, ForeignKey('chatbots.id'), nullable=True)
    chatbot = relationship('ChatBot', back_populates='knowledge_bases')
