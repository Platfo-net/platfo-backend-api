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

    facebook_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("facebook_accounts.id"),
        primary_key=False,
        nullable=True,
    )
    facebook_page_id = Column(String(255))
    instagram_page_id = Column(String(255))
    facebook_page_token = Column(String(255))
    instagram_username = Column(String(255), nullable=True)
    instagram_profile_picture_url = Column(String(1024), nullable=True)
    information = Column(JSON, nullable=True)

    facebook_account = relationship(
        "FacebookAccount", back_populates="instagram_page")
