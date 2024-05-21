from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel


class ModelBaseInfo(BaseModel):
    uuid: Optional[UUID4] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FindDateRange(BaseModel):
    created_at__lt: str
    created_at__lte: str
    created_at__gt: str
    created_at__gte: str
