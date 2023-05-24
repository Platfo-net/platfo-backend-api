from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Edge(Base):
    __tablename__ = 'bot_builder_edges'
    from_id = Column(
        UUID(as_uuid=True),
        nullable=True,
    )
    to_id = Column(
        UUID(as_uuid=True),
        nullable=True,
    )
    from_port = Column(
        UUID(as_uuid=True),
        nullable=True,
    )
    to_port = Column(
        UUID(as_uuid=True),
        nullable=True,
    )

    from_widget = Column(
        UUID(as_uuid=True),
        nullable=True,
    )
    text = Column(String(255), nullable=True)

    chatflow_id = Column(
        BigInteger,
        ForeignKey('bot_builder_chatflows.id'),
        nullable=True,
        index=True,
    )

    chatflow = relationship('Chatflow', back_populates='edge')
