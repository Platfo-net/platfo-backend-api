from app.db.base_class import Base
from sqlalchemy import Column, DateTime, String, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import relationship


class Credit(Base):
    __tablename__ = "credit_logs"

    module = Column(String(20), nullable=False)
    count = Column(Integer(), nullable=True)
    expires_at = Column(DateTime(), nullable=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        primary_key=False,
        nullable=False,
    )

    user = relationship("User", back_populates="credits")
