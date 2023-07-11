from typing import List

from sqlalchemy.orm import Session

from app import models


class CreditServices:
    def __init__(self, model):
        self.model: models.credit.Credit = model

    def get_by_user(self, db: Session, *, user_id: int) -> List[models.credit.Credit]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()


credit = CreditServices(models.credit.Credit)
