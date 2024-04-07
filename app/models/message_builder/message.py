

from sqlalchemy import BigInteger, Column, Date, Float, ForeignKey, String, Text , DateTime
from sqlalchemy.orm import relationship

from app.constants.message_builder_message_status import MessageStatus
from app.db.base_class import Base
import datetime

class MessageBuilderMessage(Base):
    __tablename__ = 'message_builder_messages'

    title = Column(String(255), nullable=True)
    url = Column(String(512), nullable=True)
    short_url = Column(String(128), nullable=True, index=True)

    message_text = Column(Text, nullable=True)
    image = Column(String(256), nullable=True)

    status = Column(String(16), nullable=True, default=MessageStatus.BUILDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    telegram_chat_id = Column(BigInteger, nullable=True, index=True)
