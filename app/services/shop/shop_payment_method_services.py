from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models


class ShopPaymentMethodServices:
    def __init__(self, model):
        self.model: models.shop.ShopShopPaymentMethod = model

    def create(self, db: Session, *, shop_id: int, payment_method_id: int):
        db_obj = self.model(
            shop_id=shop_id,
            payment_method_id=payment_method_id,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_shop(
        self, db: Session, *, shop_id: int
    ) -> List[models.shop.ShopShopPaymentMethod]:
        return (
            db.query(self.model)
            .filter(self.model.shop_id == shop_id)
            .join(self.model.payment_method).all()
        )

    def get_by_uuid(
        self, db: Session, *, uuid: UUID4
    ) -> Optional[models.shop.ShopShopPaymentMethod]:
        return (
            db.query(self.model)
            .filter(self.model.uuid == uuid)
            .join(self.model.payment_method)
            .first()
        )

    def change_is_active(
            self,
            db: Session,
            *,
            obj_in: models.shop.ShopShopPaymentMethod,
            is_active: bool
    ) -> models.shop.ShopShopPaymentMethod:
        obj_in.is_active = is_active
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def edit_information(
            self,
            db: Session,
            *,
            obj_in: models.shop.ShopShopPaymentMethod,
            information: dict
    ) -> models.shop.ShopShopPaymentMethod:
        obj_in.information = information
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in


shop_payment_method = ShopPaymentMethodServices(models.shop.ShopShopPaymentMethod)
