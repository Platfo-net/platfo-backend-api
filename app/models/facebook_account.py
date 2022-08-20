from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class FacebookAccount(Base):

    __tablename__ = "facebook_accounts"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    facebook_user_long_lived_token = Column(String(255), nullable=True)
    facebook_user_id = Column(String(255), nullable=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=False,
        nullable=True,
    )

    user = relationship(
        "User", back_populates="facebook_account")

    instagram_page = relationship(
        "InstagramPage", back_populates="facebook_account")
