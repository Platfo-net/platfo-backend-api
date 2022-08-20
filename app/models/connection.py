from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Connection(Base):

    __tablename__ = "connections"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    application_name = Column(String(255), nullable=True)

    account_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # it can be instagram page or any other platform page

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("account_id", "application_name"),
    )

    user = relationship("User", back_populates="connection")

    connection_chatflow = relationship(
        "ConnectionChatflow", back_populates="connection")
