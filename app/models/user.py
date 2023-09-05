import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        String, UniqueConstraint)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    """
    Database Model for an application user
    """

    __tablename__ = 'users'

    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    phone_number = Column(String(13), nullable=True)
    phone_country_code = Column(String(5), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=False)
    is_email_verified = Column(Boolean(), default=False)
    profile_image = Column(String(255), nullable=True)
    role_id = Column(
        BigInteger,
        ForeignKey('roles.id'),
        primary_key=False,
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    role = relationship('Role', back_populates='users')

    instagram_pages = relationship('InstagramPage', back_populates='user')
    telegram_bots = relationship('TelegramBot', back_populates='user')

    connections = relationship('Connection', back_populates='user')
    chatflows = relationship('Chatflow', back_populates='user')

    user_notifications = relationship('NotificationUser', back_populates='user')

    content = relationship('Content', back_populates='user')

    campaigns = relationship('Campaign', back_populates='user')
    invoices = relationship('Invoice', back_populates='user')
    credit_logs = relationship('CreditLog', back_populates='user')
    credits = relationship('Credit', back_populates='user')
    messages = relationship('Message', back_populates='user')
    leads = relationship('Lead', back_populates='user')

    shop_categories = relationship('ShopCategory', back_populates='user')
    shop_products = relationship('ShopProduct', back_populates='user')
    shops = relationship('ShopShop', back_populates='user')

    __table_args__ = (
        UniqueConstraint(
            'phone_country_code',
            'phone_number',
            name='_phone_number_phone_code_unique_constraint',
        ),
    )
