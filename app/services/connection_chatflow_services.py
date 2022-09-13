from pydantic import UUID4
from app import models, schemas
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder


class ConnectionChatflowServices:
    def __init__(self, model):
        self.model = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.ConnectionChatflowCreate,
        connection_id: UUID4
    ):
        db_obj = self.model(**jsonable_encoder(obj_in),
                            connection_id=connection_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def get_by_connection_id(self, db: Session, *, connection_id: UUID4):
        return db.query(self.model).filter(
            self.model.connection_id == connection_id
        )

    def remove_by_connection_id(self, db: Session, *, connection_id: UUID4):
        return db.query(self.model).filter(
            self.model.connection_id == connection_id
        ).delete()

    def remove_by_connection_id_accounts(self, db: Session, *, connection_id: UUID4):
        db_obj = db.query(self.model).filter(
            self.model.connection_id == connection_id
        ).first()
        db.delete(db_obj)
        db.commit()
        return db_obj

    def get_connection_chatflow_by_connection_and_trigger(
        self,
        db: Session,
        *,
        connection_id: UUID4,
        trigger_id: UUID4
    ):
        return db.query(self.model).filter(
            self.model.connection_id == connection_id,
            self.model.trigger_id == trigger_id
        ).first()


connection_chatflow = ConnectionChatflowServices(models.ConnectionChatflow)
