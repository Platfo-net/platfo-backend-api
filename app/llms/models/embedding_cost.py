from sqlalchemy import BigInteger, Column, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.llms.models.base import WithDates


class EmbeddingCost(Base, WithDates):
    __tablename__ = 'embedding_costs'

    cost_usd = Column(Float, nullable=True)
    total_tokens = Column(BigInteger, nullable=True)
    knowledgebase_id = Column(BigInteger, ForeignKey('knowledgebase.id'), nullable=True)
    knowledgebase = relationship('KnowledgeBase', back_populates='embedding_costs')
