from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class TelegramOrderServices:
    def __init__(self, model):
        self.model: models.shop.ShopTelegramOrder = model

    def create(
        self,
        db: Session,
        *,
        order_id: int,
    ) -> models.shop.ShopTelegramOrder:
        db_obj = self.model(
            order_id=order_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_message_info(
        self,
        db: Session,
        *,
        telegram_order_id: int,
        bot_message_id: int,
        message_reply_to_id: int,
        support_bot_message_id: int,
    ) -> None:
        db.query(self.model).filter(self.model.id == telegram_order_id).update({
            "bot_message_id": bot_message_id,
            "message_reply_to_id": message_reply_to_id,
            "support_bot_message_id": support_bot_message_id,
        })
        db.commit()

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4
    ) -> models.shop.ShopPaymentMethod:
        return db.query(self.model).join(self.model.shop).filter(self.model.uuid == uuid).first()

    def get(
        self,
        db: Session,
        *,
        id: int
    ) -> models.shop.ShopPaymentMethod:
        return db.query(self.model).join(self.model.shop).filter(self.model.id == id).first()


telegram_order = TelegramOrderServices(models.shop.ShopTelegramOrder)
