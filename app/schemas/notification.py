from typing import List, Optional
from pydantic import BaseModel, UUID4
from .pagination import Pagination
from datetime import datetime


class NotificationBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = False


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: UUID4
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class NotificationListApi(BaseModel):
    items: List[Notification]
    # pagination: Pagination

    class Config:
        orm_mode = True

