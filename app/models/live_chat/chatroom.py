import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.db.base_class import Base


class Chatroom(Base):
    __tablename__ = "live_chat_chatrooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    room_name = Column(String(255), nullable=True)
    chat_members = Column(ARRAY(JSON), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
