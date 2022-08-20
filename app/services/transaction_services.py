from app import models, schemas
from app.services.base import BaseServices
from sqlalchemy.orm import Session
from pydantic import UUID4


class TransactionServices(
        BaseServices[
            models.Transaction,
            schemas.TransactionCreate,
            schemas.TransactionUpdate
        ]):
    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.TransactionCreate,
        user_id: UUID4
    ) -> schemas.Transaction:
        db_obj = self.model(
            price=obj_in.price,
            status=obj_in.status,
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


transaction = TransactionServices(models.Transaction)
