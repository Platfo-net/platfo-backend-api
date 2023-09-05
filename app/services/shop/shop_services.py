from typing import List

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class ShopServices:
    def __init__(self, model):
        self.model: models.shop.ShopShop = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.ShopCreate,
        support_token: str,
        support_bot_token: str,
        user_id: int
    ) -> models.shop.ShopShop:
        db_obj = self.model(
            title=obj_in.title,
            description=obj_in.description,
            category=obj_in.category,
            user_id=user_id,
            support_token=support_token,
            support_bot_token = support_bot_token,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShop,
        obj_in: schemas.shop.ShopCreate,
    ) -> models.shop.ShopShop:
        db_obj.title = obj_in.title
        db_obj.description = obj_in.description
        db_obj.category = obj_in.category
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4
    ) -> models.shop.ShopShop:
        return db.query(self.model).filter(self.model.uuid == uuid).first()

    def get_user_shop_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4,
        user_id: int,
    ) -> models.shop.ShopShop:
        return db.query(self.model).filter(
            self.model.uuid == uuid, self.model.user_id == user_id).first()

    def get(
        self,
        db: Session,
        *,
        id: int
    ) -> models.shop.ShopShop:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int
    ) -> List[models.shop.ShopShop]:
        return db.query(self.model).filter(self.model.user_id == user_id).first()

    def get_by_support_token(
        self,
        db: Session,
        *,
        support_token: int
    ) -> models.shop.ShopShop:
        return db.query(self.model).filter(self.model.support_token == support_token).first()
    
    def set_support_account_chat_id(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShop,
        chat_id : int,
    ) -> models.shop.ShopShop:
        db_obj.support_account_chat_id = chat_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj



shop = ShopServices(models.shop.ShopShop)
