from uuid import uuid4

import inflect
from sqlalchemy import BigInteger, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr

p = inflect.engine()


@as_declarative()
class Base:
    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4)

    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(cls) -> str:
        return p.plural(cls.__name__.lower())
