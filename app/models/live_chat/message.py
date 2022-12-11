import datetime
from uuid import uuid4
from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID


class Message(Base):

    __tablename__ = "live_chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    from_page_id = Column(String(64), nullable=True , index = True)
    to_page_id = Column(String(64), nullable=True , index = True)

    content = Column(JSON, nullable=True)
    mid = Column(String(256), nullable=True)
    send_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # chatroom_id = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("live_chat_chatrooms.id"),
    #     nullable=True,
    # )
    # chatroom = relationship("Chatroom", back_populates="message")
