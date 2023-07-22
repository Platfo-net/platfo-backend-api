from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.base import BaseServices

ModelType = models.Connection
CreateSchemaType = schemas.ConnectionCreate
UpdateSchemaType = schemas.ConnectionUpdate


class ConnectionServices(BaseServices[ModelType, CreateSchemaType, UpdateSchemaType]):
    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        details: List[dict],
        account_id: int,
        user_id: int,
    ) -> Optional[ModelType]:
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            account_id=account_id,
            application_name=obj_in.application_name,
            user_id=user_id,
            details=details,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_and_account_id(
        self,
        db: Session,
        *,
        user_id: int,
        account_id: UUID4 = None,
    ) -> List[ModelType]:
        connections = db.query(self.model).filter(self.model.user_id == user_id)
        if account_id:
            connections = connections.filter(self.model.account_id == account_id)

        return connections.all()

    def update(
        self,
        db: Session,
        *,
        user_id: UUID4,
        db_obj: ModelType,
        obj_in: CreateSchemaType,
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
        self, db: Session, *, account_id: int, application_name: str
    ) -> List[ModelType]:
        return (
            db.query(self.model)
            .filter(
                self.model.account_id == account_id,
                self.model.application_name == application_name,
            )
            .all()
        )

    def get_by_application_name_and_account_id(
        self, db: Session, *, account_id: int, application_name: str
    ) -> Optional[ModelType]:
        return (
            db.query(self.model)
            .filter(
                self.model.account_id == account_id,
                self.model.application_name == application_name,
            )
            .first()
        )

    def get_connection(
        self, db: Session, *, account_id: int, application_name: str, trigger: str
    ) -> Optional[ModelType]:
        connection = self.get_by_application_name_and_account_id(
            db, account_id=account_id, application_name=application_name)
        if not connection:
            return None, None
        if not connection.details:
            return None, None
        for detail in connection.details:
            if detail["trigger"] == trigger:
                return connection, detail
        return None, None

    def is_chatflow_connected_to_page(
        self,
        db: Session,
        *,
        account_id: int,
        chatflow_id: int,
        application_name: str

    ) -> bool:
        connection = db.query(self.model).filter(
            self.model.account_id == account_id,
            self.model.application_name == application_name
        )
        if not connection:
            return False
        if not connection.details:
            return False
        for detail in connection.details:
            if detail["chatflow_id"] == chatflow_id:
                return True
        return False


connection = ConnectionServices(models.Connection)
