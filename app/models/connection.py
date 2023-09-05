from sqlalchemy import ARRAY, JSON, BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Connection(Base):
    __tablename__ = 'connections'

    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    application_name = Column(String(255), nullable=True)

    account_id = Column(
        BigInteger, nullable=True, index=True
    )  # it can be instagram page or any other platform page (telegram bot id)

    details = Column(ARRAY(JSON), nullable=True)  # {shop_id : 123456}
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True, index=True)

    user = relationship('User', back_populates='connections')
