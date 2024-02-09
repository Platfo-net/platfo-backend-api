from typing import List

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class TableServices:
    def __init__(self, model):
        self.model: models.shop.ShopOrder = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.TableCreate,
        shop_id: int,

    ) -> models.shop.ShopTable:
        db_obj = self.model(
            title=obj_in.title,
            shop_id=shop_id
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    def update(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopTable,
        obj_in: schemas.shop.TableUpdate,

    ) -> models.shop.ShopTable:
        db_obj.title = obj_in.title

        db.add(db_obj)
        db.commit()
        return db_obj

    def get(self, db: Session, *, id: int) -> models.shop.ShopTable:
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .first()
        )
        
    def get_by_shop_and_title(self, db: Session, *, shop_id: int , title: str) -> models.shop.ShopTable:
        return (
            db.query(self.model)
            .filter(self.model.title == title)
            .filter(self.model.shop_id == shop_id)
            .first()
        )

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> models.shop.ShopTable:
        return (
            db.query(self.model)
            .filter(self.model.uuid == uuid)
            .first()
        )

    def get_multi_by_shop_id(
        self, db: Session, *, shop_id: int
    ) -> List[models.shop.ShopTable]:
        return db.query(self.model).filter(self.model.shop_id == shop_id).all()

    def delete(
        self, db: Session, *, db_obj: models.shop.ShopTable
    ) -> List[models.shop.ShopTable]:
        db.delete(db_obj)
        db.commit()


table = TableServices(models.shop.ShopTable)
