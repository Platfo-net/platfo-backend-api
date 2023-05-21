from app.db.base_class import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, BigInteger, Text
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
    
    name= Column(String(128), nullable=True)
    website=Column(String(128), nullable=True)
    ig_id=Column(String(128), nullable=True)
    followers_count=Column(Integer, nullable=True)
    follows_count=Column(Integer, nullable=True)
    biography=Column(Text(), nullable=True)

    user = relationship("User", back_populates="instagram_pages")
