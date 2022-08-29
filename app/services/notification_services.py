
import math
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session
from pydantic import UUID4


class NotificationServices(
        BaseServices[
            models.Notification,
            schemas.NotificationCreate,
            schemas.NotificationUpdate
        ]):
    def get_by_multi(
            self,
            db: Session,
            *,
            page: int = 1,
            page_size: int = 20,
    ):
        notifications = db.query(self.model).order_by(
            self.model.created_at.desc()
        ).offset(
            page_size * (page-1)
        ).limit(
            page_size
        ).all()

        total_count = db.query(self.model).count()
        total_page = math.ceil(total_count/page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_page,
            total_count=total_count
        )

        return notifications, pagination

    def get_by_multi_for_user(
            self,
            db: Session,
            *,
            page: int = 1,
            page_size: int = 20,
            user_id: UUID4
    ):

        notification_user = db.query(models.NotificationUser).filter(
            models.NotificationUser.user_id == user_id
        ).with_entities(models.NotificationUser.notification_id).all()

        readed_notifications = [
            n.notification_id for n in notification_user
            if len(notification_user)
        ]

        notifications = db.query(self.model).offset(
            page_size * (page-1)).limit(page_size).all()
        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count/page_size)

        pagination = schemas.Pagination(
            page=page,
            total_pages=total_pages,
            page_size=page_size,
            total_count=total_count)

        return [schemas.NotificationListItem(
            id=notification.id,
            title=notification.title,
            description=notification.description,
            created_at=notification.created_at,
            is_readed=True
                if notification.id in readed_notifications else False
                )
                for notification in notifications
                ], pagination

    def read(self, db: Session, *, id: UUID4, user_id: UUID4):
        notification_user = models.NotificationUser(
            user_id=user_id,
            notification_id=id
        )
        db.add(notification_user)
        db.commit()
        db.refresh(notification_user)
        return None


class NotificationUserServices:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, *, notification_id: UUID4, user_id: UUID4):
        return db.query(self.model).filter(
            models.NotificationUser.notification_id == notification_id,
            models.NotificationUser.user_id == user_id
        ).first()


notification = NotificationServices(models.Notification)
notification_user = NotificationUserServices(models.NotificationUser)
