import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        String, Text)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Notification(Base):
    """
    Database Model for an application notification
    """

    __tablename__ = 'notifications'
    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)
    is_visible = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    notification_user = relationship('NotificationUser', back_populates='notification')


class NotificationUser(Base):
    __tablename__ = 'notification_users'

    user_id = Column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=True,
    )

    notification_id = Column(
        BigInteger,
        ForeignKey('notifications.id'),
        nullable=True,
    )

    user = relationship('User', back_populates='user_notifications')

    notification = relationship('Notification', back_populates='notification_user')
