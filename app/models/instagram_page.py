from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship


class InstagramPage(Base):
    __tablename__ = "instagram_pages"

    facebook_user_long_lived_token = Column(String(255), nullable=True)
    facebook_user_id = Column(String(255), nullable=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        primary_key=False,
        nullable=True,
    )
    facebook_page_id = Column(BigInteger, nullable=True, index=True)
    instagram_page_id = Column(BigInteger, nullable=True, index=True)
    facebook_page_token = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    profile_picture_url = Column(String(1024), nullable=True)
    information = Column(JSON, nullable=True)

    user = relationship("User", back_populates="instagram_page")
