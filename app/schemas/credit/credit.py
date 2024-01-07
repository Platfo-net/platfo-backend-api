

from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field


class ShopCredit(BaseModel):
    expires_at: Optional[datetime] = None
    is_expired: bool


class AddDaysCredit(BaseModel):
    days_added: int = Field(default=0, min=0)


class CreditExtend(BaseModel):
    plan_id: UUID4



class PaymentUrl(BaseModel):
    payment_url: str
