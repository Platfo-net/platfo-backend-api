from datetime import timedelta
from sqlalchemy.orm import Session
from app import models
from pydantic import UUID4


class CreditServices:
    def __init__(self, model):
        self.model = model

    def create(
        self,
        db: Session,
        *,
        user_id: UUID4,
    ) -> models.Credit:
        db_obj = self.model(user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_id(self, db: Session, *, user_id: UUID4):
        return db.query(self.model).filter(
            self.model.user_id == user_id
        ).first()

    def add_days_to_credit(
        self,
        db: Session,
        *,
        user_id: UUID4,
        days_add: int
    ):
        credit = self.get_by_user_id(db, user_id=user_id)
        credit.to_datetime += timedelta(days=days_add)
        db.add(credit)
        db.commit()
        db.refresh(credit)
        return credit


credit = CreditServices(models.Credit)
