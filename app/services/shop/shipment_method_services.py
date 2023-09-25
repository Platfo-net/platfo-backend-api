from typing import List

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class ShipmentMethodServices:
    def __init__(self, model):
        self.model: models.shop.ShopShipmentMethod = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.ShipmentMethodCreate,
        shop_id: int,
    ) -> models.shop.ShopShipmentMethod:
        db_obj = self.model(
            title=obj_in.title,
            shop_id=shop_id,
            price=obj_in.price,
            currency=obj_in.currency,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShipmentMethod,
        obj_in: schemas.shop.ShipmentMethodCreate,
    ) -> models.shop.ShopShipmentMethod:

        db_obj.title = obj_in.title
        db_obj.currency = obj_in.currency
        db_obj.price = obj_in.price

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4
    ) -> models.shop.ShopShipmentMethod:
        return db.query(self.model).join(self.model.shop).filter(self.model.uuid == uuid).first()

    def get(
        self,
        db: Session,
        *,
        id: int
    ) -> models.shop.ShopShipmentMethod:
        return db.query(self.model).join(self.model.shop).filter(self.model.id == id).first()

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int
    ) -> List[models.shop.ShopShipmentMethod]:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.shop.user_id == user_id)
            .all()
        )

    def delete(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopShipmentMethod
    ):
        db.delete(db_obj)
        db.commit()


shipment_method = ShipmentMethodServices(models.shop.ShopShipmentMethod)