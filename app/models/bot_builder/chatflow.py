import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey , BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Chatflow(Base):

    __tablename__ = "bot_builder_chatflows"

    name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
        index = True
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    node = relationship("Node", back_populates="chatflow")
    nodeui = relationship("NodeUI", back_populates="chatflow")
    edge = relationship("Edge", back_populates="chatflow")
    user = relationship("User", back_populates="chatflow")
