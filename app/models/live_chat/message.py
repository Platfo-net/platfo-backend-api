import datetime

from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Message(Base):
    __tablename__ = 'live_chat_messages'

    from_page_id = Column(BigInteger, nullable=True, index=True)
    to_page_id = Column(BigInteger, nullable=True, index=True)
    type = Column(String(32), nullable=True)
    content = Column(JSON, nullable=True)
    mid = Column(String(256), nullable=True)
    send_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )

    user = relationship('User', back_populates='messages')
