import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey , BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class User(Base):
    """
    Database Model for an application user
    """

    __tablename__ = "users"
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(13), nullable=True, unique=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)

    role_id = Column(
        BigInteger,
        ForeignKey("roles.id"),
        primary_key=False,
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    role = relationship("Role", back_populates="user")

    instagram_page = relationship("InstagramPage", back_populates="user")

    connection = relationship("Connection", back_populates="user")
    chatflow = relationship("Chatflow", back_populates="user")

    notification_user = relationship("NotificationUser", back_populates="user")

    content = relationship("Content", back_populates="user")

    campaign = relationship("Campaign", back_populates="user")
    group = relationship("Group", back_populates="user")
