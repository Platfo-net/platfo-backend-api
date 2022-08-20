from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ConnectionChatflow(Base):

    __tablename__ = "connection_chatflows"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    connection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("connections.id"),
        nullable=True,
    )

    trigger_id = Column(
        UUID(as_uuid=True),
        ForeignKey("triggers.id"),
        nullable=True,
    )

    chatflow_id = Column(
        UUID(as_uuid=True),
    )

    connection = relationship(
        "Connection", back_populates="connection_chatflow")
    trigger = relationship("Trigger", back_populates="connection_chatflow")
