from typing import List, Optional
from pydantic import BaseModel, UUID4
from .pagination import Pagination
from datetime import datetime


class NotificationBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class NotificationCreate(NotificationBase):
    is_visible: Optional[bool] = False


class NotificationUpdate(NotificationBase):
    is_visible: Optional[bool] = False


class Notification(NotificationBase):
    id: UUID4
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class NotificationListItem(NotificationBase):
    id: UUID4
    created_at: Optional[datetime] = None
    is_readed: Optional[bool] = True

    class Config:
        orm_mode = True


class NotificationListApi(BaseModel):
    items: List[NotificationListItem]
    pagination: Pagination

    class Config:
        orm_mode = True
