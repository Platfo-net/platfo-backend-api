from typing import List, Optional
from pydantic import UUID4
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session


ModelType = models.Connection
CreateSchemaType = schemas.ConnectionCreate
UpdateSchemaType = schemas.ConnectionUpdate


class ConnectionServices(
    BaseServices
    [
        ModelType,
        CreateSchemaType,
        UpdateSchemaType
    ]
):
    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        user_id: UUID4
    ) -> Optional[ModelType]:

        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            account_id=obj_in.account_id,
            application_name=obj_in.application_name,
            user_id=user_id,
            details=obj_in.details

        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_and_account_id(
        self,
        db: Session,
        *,
        user_id: UUID4,
        account_id: UUID4 = None,
    ) -> List[ModelType]:
        connections = db.query(self.model).filter(
            self.model.user_id == user_id
        )
        if account_id:
            connections = connections.filter(
                self.model.account_id == account_id)

        return connections.all()

    def update(self, db: Session, *, user_id: UUID4,
               db_obj: ModelType, obj_in: CreateSchemaType
               ) -> Optional[ModelType]:
        db_obj.user_id = user_id
        db_obj.account_id = obj_in.account_id
        db_obj.application_name = obj_in.application_name
        db_obj.name = obj_in.name
        db_obj.description = obj_in.description
        db_obj.details = obj_in.details

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_page_connections(
        self,
        db: Session,
        *,
        account_id: str,
        application_name: str
    ) -> List[ModelType]:
        return db.query(self.model).filter(
            self.model.account_id == account_id,
            self.model.application_name == application_name
        ).all()

    def get_by_application_name_and_account_id(
        self,
        db: Session,
        *,
        account_id: str,
        application_name: str
    ) -> Optional[ModelType]:
        return db.query(self.model).filter(
            self.model.account_id == account_id,
            self.model.application_name == application_name
        ).first()


connection = ConnectionServices(models.Connection)
