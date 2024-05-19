from sqlalchemy import ARRAY, JSON, BigInteger, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.llms.models.base import WithDates


class KnowledgeBase(Base, WithDates):
    __tablename__ = 'knowledgebase'

    name = Column(String(255), nullable=False)
    metadatas = Column(JSON(), nullable=True)
    manual_input = Column(Text(), nullable=True)
    type = Column(String(40), nullable=True)
    file_path = Column(String(255), nullable=True)
    urls = Column(ARRAY(String), nullable=True)
    source_link = Column(String(255), nullable=True)
    chatbot_id = Column(BigInteger, ForeignKey('chatbots.id'), nullable=True)
    chatbot = relationship('ChatBot', back_populates='knowledge_bases')
    embedding_costs = relationship('EmbeddingCost', back_populates='knowledgebase')
