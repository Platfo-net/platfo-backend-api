from uuid import uuid4
from app.db.base_class import Base
from sqlalchemy import Column, String,\
    ForeignKey, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship


class Edge(Base):
    __tablename__ = "edges"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    from_id = Column(
        UUID(as_uuid=True)
    )
    to_id = Column(
        UUID(as_uuid=True)
    )
    from_port = Column(
        UUID(as_uuid=True)
    )
    to_port= Column(
        UUID(as_uuid=True)
    )

    chatflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chatflows.id"),
        nullable=True,
    )

    chatflow = relationship("Chatflow", back_populates="edge")

