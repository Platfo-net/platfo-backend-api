from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey, JSON, Boolean, Integer, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship


class NodeUI(Base):
    __tablename__ = "bot_builder_nodeuies"

    text = Column(String(255), nullable=True)
    width = Column(Integer(), nullable=True)
    height = Column(Integer(), nullable=True)

    data = Column(JSON, nullable=True)
    ports = Column(ARRAY(JSON), nullable=True)

    has_delete_action = Column(Boolean(), nullable=True)
    has_edit_action = Column(Boolean(), nullable=True)

    chatflow_id = Column(
        BigInteger,
        ForeignKey("bot_builder_chatflows.id"),
        nullable=True,
        index=True
    )

    chatflow = relationship("Chatflow", back_populates="nodeui")
