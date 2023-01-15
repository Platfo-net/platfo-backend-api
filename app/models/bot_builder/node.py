from uuid import uuid4
from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey, JSON, Boolean , BigInteger
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship


class Node(Base):

    __tablename__ = "bot_builder_nodes"
    title = Column(String(255), nullable=True)
    chatflow_id = Column(
        BigInteger,
        ForeignKey("bot_builder_chatflows.id"),
        nullable=True,
        index = True
    )
    from_widget = Column(ARRAY(UUID), nullable=True)
    widget = Column(JSON, nullable=True)
    quick_replies = Column(ARRAY(JSON), nullable=True)
    is_head = Column(Boolean, default=False)
    chatflow = relationship("Chatflow", back_populates="node")
