import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Boolean, Column, \
    DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Notification(Base):
    """
    Database Model for an application notification
    """

    __tablename__ = "notifications"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)
    is_visible = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    notification_user = relationship(
        "NotificationUser", back_populates="notification")


class NotificationUser(Base):
    """
        Model for saving users readed notifications
    """
    __tablename__ = "notification_users"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    notification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id"),
        nullable=True,
    )

    user = relationship(
        "User", back_populates="notification_user")

    notification = relationship(
        "Notification", back_populates="notification_user")
