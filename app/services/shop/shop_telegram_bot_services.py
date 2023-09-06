from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class ShopTelegramBotServices:
    def __init__(self, model):
        self.model: models.shop.ShopShopTelegramBot = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.ShopTelegramBotCreate,
    ) -> models.shop.ShopShopTelegramBot:
        db_obj = self.model(
            support_token=obj_in.support_token,
            support_bot_token=obj_in.support_bot_token,
            shop_id=obj_in.shop_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_support_token(
        self,
        db: Session,
        *,
        support_token: str
    ) -> models.shop.ShopShopTelegramBot:
        return db.query(self.model).filter(self.model.support_token == support_token).first()

    def get_by_support_bot_token(
        self,
        db: Session,
        *,
        support_bot_token: str
    ) -> models.shop.ShopShopTelegramBot:
        return db.query(self.model).filter(
            self.model.support_bot_token == support_bot_token).first()

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
        shop_id: UUID4
    ) -> models.shop.ShopShopTelegramBot:
        return db.query(self.model).filter(self.model.shop_id == shop_id).first()

    def connect_telegram_bot(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShopTelegramBot,
        telegram_bor_id: int,
    ) -> models.shop.ShopShopTelegramBot:
        db_obj.shop_id = telegram_bor_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


shop_telegram_bot = ShopTelegramBotServices(models.shop.ShopShopTelegramBot)
