from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import paginate


class ChatflowServices:
    def __init__(self, model):
        self.model: models.bot_builder.Chatflow = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.bot_builder.ChatflowCreate,
        user_id: int,
    ) -> models.bot_builder.Chatflow:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: models.bot_builder.Chatflow,
        obj_in: schemas.bot_builder.chatflow.ChatflowUpdate,
    ) -> models.bot_builder.Chatflow:
        db_obj.name = obj_in.name,
        db.add(db_obj)
        db.commit()
        return db_obj

    def get(self, db: Session, *, id: int):
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .first()
        )

    def get_by_uuid(self, db: Session, *, uuid: UUID4, user_id: int):
        return db.query(self.model).filter(
            self.model.uuid == uuid,
            self.model.user_id == user_id,
        ).first()

    def get_user_chatflow_by_uuid(self, db: Session, *, uuid: UUID4, user_id: int):
        return db.query(self.model).filter(
            self.model.uuid == uuid,
            self.model.user_id == user_id
        ).first()

    def get_multi(
        self, db: Session, *, user_id: int, page: int = 1, page_size: int = 20
    ):
        chatflows = (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(page_size * (page - 1))
            .limit(page_size)
            .all()
        )

        total_count = db.query(self.model).filter(self.model.user_id == user_id).count()

        return paginate(total_count, page, page_size), chatflows

    def delete(
        self,
        db: Session,
        *,
        id: int,
    ):
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        db.delete(db_obj)
        db.commit()

    def delete_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4,
    ):
        db_obj = db.query(self.model).filter(self.model.uuid == uuid).first()
        db.delete(db_obj)
        db.commit()


chatflow = ChatflowServices(models.bot_builder.Chatflow)
