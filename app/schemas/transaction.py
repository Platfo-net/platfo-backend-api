from typing import Optional

from pydantic import UUID4, BaseModel


from app.constants.transaction_status import TransactionStatus


class TransactionBase(BaseModel):
    price: Optional[int] = None
    status: Optional[str] = TransactionStatus.PENDING["value"]


class TransactionCreate(TransactionBase):
    plan_id: Optional[UUID4]


class TransactionUpdate(TransactionBase):
    pass


class TransactionInDBBase(TransactionBase):
    id: UUID4
    user_id: UUID4

    class Config:
        orm_mode = True


class Transaction(TransactionInDBBase):
    pass


class TransactionInDB(TransactionInDBBase):
    pass
