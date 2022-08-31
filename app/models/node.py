from uuid import uuid4
from app.db.base_class import Base
from sqlalchemy import Column, String,\
    ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship


class Node(Base):

    __tablename__ = "nodes"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title = Column(String(255), nullable=True)
    chatflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chatflows.id"),
        primary_key=False,
        nullable=True,
    )
    from_widget = Column(ARRAY(UUID), nullable=True)
    widget = Column(JSON, nullable=True)
    quick_replies = Column(ARRAY(JSON), nullable=True)
    is_head = Column(Boolean, default=False)
    chatflow = relationship(
        "Chatflow", back_populates="node")
