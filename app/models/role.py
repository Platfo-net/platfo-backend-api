from app.db.base_class import Base
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "roles"
    name = Column(String(100))
    description = Column(Text)
    persian_name = Column(String(100), nullable=True)

    users = relationship("User", back_populates="role")
