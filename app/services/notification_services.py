from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session


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
            skip: int = 0,
            limit: int = 20,
    ):

        notifications = db.query(self.model).offset(skip).limit(limit).all()
        n = jsonable_encoder(notifications)
        return n


notification = NotificationServices(models.Notification)
