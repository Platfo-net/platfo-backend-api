from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __name__: str
