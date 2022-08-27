import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class NotificationUser(Base):

    __tablename__ = "notification_users"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    notification_id =  Column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id"),
        nullable=True,
    )


    user = relationship(
        "User", back_populates="notification_user")

    notification = relationship(
        "Notification", back_populates="notification_user")
