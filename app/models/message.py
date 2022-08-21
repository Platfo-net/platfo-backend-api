import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, UniqueConstraint,JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Message(Base):

    __tablename__ = "Messages"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    from_page_id = Column(String(64), nullable=True)
    to_page_id = Column(String(64), nullable=True)

    content = Column(JSON, nullable=True)
    send_at = Column(DateTime, default=datetime.datetime.utcnow)


    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )



