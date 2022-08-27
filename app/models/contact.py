import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID


class Contact(Base):

    __tablename__ = "contacts"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    contact_igs_id = Column(String(64), nullable=True)
    user_page_id = Column(String(64), nullable=True)

    last_message = Column(JSON, nullable=True)
    last_message_at = Column(DateTime, default=datetime.datetime.utcnow)

    information = Column(JSON, nullable=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
