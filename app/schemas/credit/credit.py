

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Credit(BaseModel):
    module: str
    expires_at: Optional[datetime] = None
    count: Optional[int] = None
