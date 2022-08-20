

import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.constants.transaction_status import TransactionStatus


class Transaction(Base):

    __tablename__ = "transactions"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=False,
        nullable=True,
    )

    price = Column(DateTime, default=datetime.datetime.utcnow)

    status = Column(String(10), default=TransactionStatus.PENDING["value"])
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
    )

    user = relationship(
        "User", back_populates="transaction")
