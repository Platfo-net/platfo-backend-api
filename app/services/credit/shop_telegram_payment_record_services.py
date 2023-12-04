from typing import Optional

from sqlalchemy.orm import Session

from app import models
from app.core.unit_of_work import UnitOfWork


class ShopTelegramPaymentRecordServices:
    def __init__(self, model):
        self.model: models.credit.CreditShopTelegramPaymentRecord = model

    def create(self, db: Session, *, shop_id: int, plan_id: int , amount : int):
        db_obj = self.model(
            shop_id=shop_id,
            plan_id=plan_id,
            amount = amount,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def change_status(
            self, uow: UnitOfWork, *,
            db_obj: models.credit.CreditShopTelegramPaymentRecord,
            status: str
    ):
        db_obj.status = status
        uow.add(db_obj)
        return db_obj

    def get(
        self, db: Session, *, id: int
    ) -> Optional[models.credit.CreditShopTelegramPaymentRecord]:
        return db.query(self.model).filter(
            self.model.id == id,
        ).first()

    def add_ref_id(
        self, uow: UnitOfWork, *,
        db_obj: models.credit.CreditShopTelegramPaymentRecord,
        ref_id: int
    ) -> Optional[models.credit.CreditShopTelegramPaymentRecord]:
        db_obj.ref_id = ref_id
        uow.add(db_obj)
        return db_obj

    def add_authority(
        self, db: Session, *,
        db_obj: models.credit.CreditShopTelegramPaymentRecord,
        authority: str
    ) -> Optional[models.credit.CreditShopTelegramPaymentRecord]:
        db_obj.payment_authority = authority
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


shop_telegram_payment_record = ShopTelegramPaymentRecordServices(
    models.credit.CreditShopTelegramPaymentRecord)
