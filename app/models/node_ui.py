from uuid import uuid4
from app.db.base_class import Base
from sqlalchemy import Column, String,\
    ForeignKey, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship


class NodeUI(Base):
    __tablename__ = "nodeuies"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    text = Column(String(255), nullable=True)
    width = Column(Integer(), nullable=True)
    height = Column(Integer(), nullable=True)

    data = Column(JSON, nullable=True)
    ports = Column(ARRAY(JSON), nullable=True)

    has_delete_action = Column(Boolean(), nullable=True)
    has_edit_action = Column(Boolean(), nullable=True)

    chatflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chatflows.id"),
        nullable=True,
    )

    chatflow = relationship("Chatflow", back_populates="nodeui")
