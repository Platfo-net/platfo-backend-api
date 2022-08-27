from pydantic import UUID4
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session


class ConnectionServices(
    BaseServices
    [
        models.Connection,
        schemas.ConnectionCreate,
        schemas.ConnectionUpdate
    ]
):
    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.ConnectionCreate,
        user_id: UUID4
    ):
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            account_id=obj_in.account_id,
            application_name=obj_in.application_name,
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_id(
        self,
        db: Session,
        *,
        user_id: UUID4,
        skip: int = 0,
        limit: int = 20,
        account_id: UUID4 = None,
    ):
        connections = db.query(self.model).filter(
            self.model.user_id == user_id
        )

        if account_id:
            connections = connections.filter(
                self.model.account_id == account_id)

        return connections.offset(skip).limit(limit)

    def update(self, db: Session, *, user_id: UUID4,
               db_obj: models.Connection, obj_in: schemas.ConnectionCreate):
        db_obj.user_id = user_id
        db_obj.account_id = obj_in.account_id
        db_obj.application_name = obj_in.application_name
        db_obj.name = obj_in.name
        db_obj.description = obj_in.description

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_page_connection(self, db: Session, *,
                            account_id: str, application_name: str
                            ):
        return db.query(self.model).filter(
            self.model.account_id == account_id,
            self.model.application_name == application_name
        ).all()


connection = ConnectionServices(models.Connection)
