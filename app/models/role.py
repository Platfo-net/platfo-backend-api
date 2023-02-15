from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "roles"
    name = Column(String(100))
    description = Column(Text)
    persian_name = Column(String(100), nullable=True)
    user = relationship("User", back_populates="role")
