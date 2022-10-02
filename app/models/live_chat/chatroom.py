import datetime
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String,\
    DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Chatroom(Base):
    __tablename__ = "chatrooms"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    room_name = Column(String(255), nullable=True)
    chat_members = Column(ARRAY(JSON), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    message = relationship(
           "Message",
           back_populates="chatroom",
           cascade="all,delete"
    )
    user = relationship("User", back_populates="chatroom")
