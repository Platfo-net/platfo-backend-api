# from typing import Optional

from typing import List
from app.services.base import BaseServices
from sqlalchemy.orm import Session
from app import models, schemas
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4


class ChatflowServices(
    BaseServices[
        models.bot_builder.Chatflow,
        schemas.bot_builder.ChatflowCreate,
        schemas.bot_builder.ChatflowUpdate,
    ]
):
    def create(
        self, db: Session, *, obj_in: schemas.bot_builder.ChatflowCreate, user_id: UUID4
    ) -> models.bot_builder.Chatflow:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: UUID4, user_id: UUID4):
        return (
            db.query(self.model)
            .filter(self.model.id == id, self.model.user_id == user_id)
            .first()
        )

    def get_multi(
        self, db: Session, *, user_id: UUID4, skip: int = 0, limit: int = 100
    ) -> List[models.bot_builder.Chatflow]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_chatflow(
        self,
        db: Session,
        *,
        id: str,
    ):
        db_obj = db.query(self.model).filter(
            self.model.id == id).first()
        # connections = db.query(models.Connection)\
        #     .filter(models.Connection.user_id == db_obj.user_id).all()
        # for connection in connections:
        #     for detail in connection.details:
        #         if detail['chatflow_id'] == str(db_obj.id):
        #             connection_obj = db.query(models.Connection)\
        #                 .filter(models.Connection.id == connection.id).first()
        #             db.delete(connection_obj)
        db.delete(db_obj)
        db.commit()


chatflow = ChatflowServices(models.bot_builder.Chatflow)
