from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Trigger(Base):

    __tablename__ = "triggers"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    name = Column(String(255), nullable=True)
    persian_name = Column(String(255), nullable=True)
    platform = Column(String(255), nullable=True)

    connection_chatflow = relationship(
        "ConnectionChatflow", back_populates="trigger")
