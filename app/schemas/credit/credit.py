

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ShopCredit(BaseModel):
    expires_at: Optional[datetime] = None
    is_expired: bool


class AddDaysCredit(BaseModel):
    days_added: int = Field(default=0, min=0)
