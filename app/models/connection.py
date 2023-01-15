from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, ARRAY, JSON, BigInteger
from sqlalchemy.orm import relationship


class Connection(Base):

    __tablename__ = "connections"

    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    application_name = Column(String(255), nullable=True)

    account_id = Column(
        BigInteger, nullable=True, index=True
    )  # it can be instagram page or any other platform page

    details = Column(ARRAY(JSON), nullable=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    user = relationship("User", back_populates="connection")
