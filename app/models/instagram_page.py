from uuid import uuid4
from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class InstagramPage(Base):

    __tablename__ = "instagram_pages"
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
    facebook_page_id = Column(String(255) , nullable=True)
    instagram_page_id = Column(String(255) , nullable=True)
    facebook_page_token = Column(String(255) , nullable=True)
    instagram_username = Column(String(255), nullable=True)
    instagram_profile_picture_url = Column(String(1024), nullable=True)
    information = Column(JSON, nullable=True)

    user = relationship(
        "User", back_populates="facebook_account")
