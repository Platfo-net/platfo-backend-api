from typing import List

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class CategoryServices:
    def __init__(self, model):
        self.model: models.shop.ShopCategory = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.CategoryCreate,
        user_id: int
    ) -> models.shop.ShopCategory:
        db_obj = self.model(
            title=obj_in.title,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopCategory,
        obj_in: schemas.shop.CategoryCreate,
        user_id: int
    ) -> models.shop.ShopCategory:
        db_obj.title = obj_in.title
        db_obj.user_id = user_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4
    ) -> models.shop.ShopCategory:
        return db.query(self.model).filter(self.model.uuid == uuid).first()

    def get(
        self,
        db: Session,
        *,
        id: int
    ) -> models.shop.ShopCategory:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int
    ) -> List[models.shop.ShopCategory]:
        return db.query(self.model).filter(self.model.user_id == user_id).first()


category = CategoryServices(models.shop.ShopCategory)
