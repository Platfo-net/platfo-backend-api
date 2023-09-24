from uuid import uuid4

from sqlalchemy import BigInteger, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4)

    __name__: str
