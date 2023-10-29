from sqlalchemy.orm import Session

from app import models


class ShopTelegramPaymentRecordServices:
    def __init__(self, model):
        self.model: models.credit.CreditShopTelegramPaymentRecord = model

    def create(self, db: Session, *, shop_id: int, plan_id: int, reply_to_message_id: int):
        db_obj = self.model(
            shop_id=shop_id,
            plan_id=plan_id,
            reply_to_message_id=reply_to_message_id

        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


shop_telegram_payment_record = ShopTelegramPaymentRecordServices(
    models.credit.CreditShopTelegramPaymentRecord)
