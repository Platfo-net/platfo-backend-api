from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.unit_of_work import UnitOfWork


class ShopTelegramBotServices:
    def __init__(self, model):
        self.model: models.shop.ShopShopTelegramBot = model

    def create(
        self,
        uow: UnitOfWork,
        *,
        obj_in: schemas.shop.ShopTelegramBotCreate,
    ) -> models.shop.ShopShopTelegramBot:
        db_obj = self.model(
            support_token=obj_in.support_token,
            support_bot_token=obj_in.support_bot_token,
            shop_id=obj_in.shop_id,
        )
        uow.add(db_obj)
        return db_obj

    def get_by_support_token(
        self,
        db: Session,
        *,
        support_token: str
    ) -> models.shop.ShopShopTelegramBot:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.support_token == support_token)
            .first()
        )

    def get_by_support_bot_token(
        self,
        db: Session,
        *,
        support_bot_token: str
    ) -> models.shop.ShopShopTelegramBot:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.support_bot_token == support_bot_token)
            .first()
        )

    def get_by_telegram_bot_id(
        self,
        db: Session,
        *,
        telegram_bot_id: int
    ) -> models.shop.ShopShopTelegramBot:
        return (
            db.query(self.model)
            .join(self.model.telegram_bot)
            .filter(self.model.telegram_bot_id == telegram_bot_id)
            .first()
        )

    def set_support_account_chat_id(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShopTelegramBot,
        chat_id: int,
    ) -> models.shop.ShopShopTelegramBot:
        db_obj.support_account_chat_id = chat_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def verify_support_account(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShopTelegramBot,
    ) -> models.shop.ShopShopTelegramBot:
        db_obj.is_support_verified = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_shop_id(
        self,
        db: Session,
        *,
        shop_id: int
    ) -> Optional[models.shop.ShopShopTelegramBot]:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.shop_id == shop_id)
            .first()
        )

    def connect_telegram_bot(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShopTelegramBot,
        telegram_bot_id: int,
    ) -> models.shop.ShopShopTelegramBot:
        db_obj.telegram_bot_id = telegram_bot_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_chat_id(
        self,
        db: Session,
        *,
        chat_id: int,
    ) -> models.shop.ShopShopTelegramBot:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.support_account_chat_id == chat_id)
            .first()
        )

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4,
    ) -> models.shop.ShopShopTelegramBot:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.uuid == uuid)
            .first()
        )

    def get(
        self,
        db: Session,
        *,
        id: int,
    ) -> models.shop.ShopShopTelegramBot:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.id == id)
            .first()
        )

    def all(
        self,
        db: Session,
    ) -> models.shop.ShopShopTelegramBot:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .join(self.model.telegram_bot)
            .all()
        )

    def get_multi_by_shop_ids(
        self, db: Session, *, shop_ids: List[int]
    ) -> List[models.shop.ShopShopTelegramBot]:
        return (
            db.query(self.model)
            .filter(self.model.shop_id.in_(shop_ids))
            .join(self.model.telegram_bot)
            .all()
        )


shop_telegram_bot = ShopTelegramBotServices(models.shop.ShopShopTelegramBot)
