
from typing import List
from app.services.base import BaseServices
from sqlalchemy.orm import Session
from app import models, schemas
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4


class ChatroomServices(
    BaseServices
    [
        models.live_chat.Chatroom,
        schemas.live_chat.ChatroomCreate,
        schemas.live_chat.ChatroomUpdate
    ]
):
    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.live_chat.ChatroomCreate,
        user_id: UUID4
    ) -> models.live_chat.Chatroom:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(
        self,
        db: Session,
        id: UUID4,
        user_id: UUID4
    ):
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.user_id == user_id
        ).first()

    def get_multi(
        self,
        db: Session,
        *,
        user_id: UUID4,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.live_chat.Chatroom]:
        return db.query(self.model).filter(
            self.model.user_id == user_id
        ).offset(skip).limit(limit).all()


chatroom = ChatroomServices(models.live_chat.Chatroom)
