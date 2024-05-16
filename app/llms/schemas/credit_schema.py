from datetime import datetime, timedelta
from typing import Optional

from pydantic import UUID4, BaseModel, computed_field


class ChatBotCreditSchema(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None

    class Config:
        orm_mode = True


class ChatBotTransactionItem(BaseModel):
    uuid: Optional[UUID4]
    amount: Optional[float] = None
    currency: Optional[str] = None
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    is_paid: Optional[bool] = None

    @computed_field
    @property
    def can_pay(self) -> bool:
        d = datetime.now() - timedelta(days=2)
        return self.created_at > d and not self.is_paid


class ChatBotTransactionCreate(BaseModel):
    user_id: int
    amount: float
    currency: Optional[str] = None


class TransactionUpdate(BaseModel):
    is_paid: bool
    payed_at: datetime


class ChatBotCreditCreate(BaseModel):
    amount: float
    currency: str
    user_id: int
