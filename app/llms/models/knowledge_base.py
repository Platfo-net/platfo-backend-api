from sqlalchemy import Column, ForeignKey, String, BigInteger, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from app.llms.models.base import Base


class KnowledgeBaseType(enum.Enum):
    PDF = "pdf"
    TXT = "txt"


class KnowledgeBase(Base):
    __tablename__ = 'knowledgebase'

    name = Column(String(255), nullable=False)
    metadatas = Column(JSON(), nullable=True)
    type = Column(Enum(KnowledgeBaseType), nullable=True)
    file_path = Column(String(255), nullable=True)
    chatbot_id = Column(BigInteger, ForeignKey('chatbots.id'), nullable=True)
    chatbot = relationship('ChatBot', back_populates='knowledge_bases')
