from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel

from .pagination import Pagination


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
        from_attributes = True


class NotificationListItem(NotificationBase):
    id: UUID4
    created_at: Optional[datetime] = None
    is_read: Optional[bool] = True

    class Config:
        from_attributes = True


class NotificationListApi(BaseModel):
    items: List[NotificationListItem]
    pagination: Pagination

    class Config:
        from_attributes = True
