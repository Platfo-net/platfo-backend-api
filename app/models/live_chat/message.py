import datetime
from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, JSON, DateTime, BigInteger


class Message(Base):
    __tablename__ = "live_chat_messages"

    from_page_id = Column(BigInteger, nullable=True, index=True)
    to_page_id = Column(BigInteger, nullable=True, index=True)

    content = Column(JSON, nullable=True)
    mid = Column(String(256), nullable=True)
    send_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
    )
