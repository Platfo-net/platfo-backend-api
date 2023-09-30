from datetime import datetime, timedelta
from pydantic import UUID4

from sqlalchemy.orm import Session

from app import models


class ShopCreditServices:
    def __init__(self, model):
        self.model: models.credit.ShopCredit = model

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> models.credit.ShopCredit:
        return db.query(self.model).filter(self.model.uuid == uuid).all()

    def get_by_shop_id(self, db: Session, *, shop_id: int) -> models.credit.ShopCredit:
        return db.query(self.model).filter(self.model.shop_id == shop_id).first()

    def add_shop_credit(
            self,
            db: Session,
            *,
            db_obj: models.credit.ShopCredit,
            days: int
    ) -> models.credit.ShopCredit:
        if db_obj.expires_at < datetime.now():
            db_obj.expires_at = datetime.now()
        db_obj.expires_at = db_obj.expires_at + timedelta(days=days)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create(self, db: Session, *, shop_id: int, free_days: int) -> models.credit.ShopCredit:
        db_obj = self.model(
            shop_id=shop_id,
            expires_at=datetime.now() + timedelta(days=free_days),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


shop_credit = ShopCreditServices(models.credit.ShopCredit)
