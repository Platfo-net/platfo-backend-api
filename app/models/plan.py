

import datetime
from uuid import uuid4

from app.db.base_class import Base
from sqlalchemy import Boolean, Column, Integer, Text
from sqlalchemy.dialects.postgresql import UUID


class Plan(Base):

    __tablename__ = "plans"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    price = Column(Integer, default=datetime.datetime.utcnow)
    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    days_add = Column(Integer, default=0)
