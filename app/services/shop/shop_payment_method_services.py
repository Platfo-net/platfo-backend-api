from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models
from app.core.unit_of_work import UnitOfWork


class ShopPaymentMethodServices:
    def __init__(self, model):
        self.model: models.shop.ShopShopPaymentMethod = model

    def create(self, uow: UnitOfWork, *, shop_id: int, payment_method_id: int):
        db_obj = self.model(
            shop_id=shop_id,
            payment_method_id=payment_method_id,
            is_active=True,
            information={},
        )
        uow.add(db_obj)
        return db_obj

    def get_multi_by_shop(
        self, db: Session, *, shop_id: int, is_active: Optional[bool] = None
    ) -> List[models.shop.ShopShopPaymentMethod]:
        conditions = [self.model.shop_id == shop_id]
        if is_active is not None:
            conditions.append(self.model.is_active == is_active)

        return (db.query(self.model)
                .filter(*conditions)
                .join(self.model.payment_method).all())

    def get_by_uuid(
        self, db: Session, *, uuid: UUID4
    ) -> Optional[models.shop.ShopShopPaymentMethod]:
        return (
            db.query(self.model)
            .filter(self.model.uuid == uuid)
            .join(self.model.payment_method, isouter=True)
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

    def get(
            self,
            db: Session,
            *,
            id: int
    ) -> Optional[models.shop.ShopShopPaymentMethod]:
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .join(self.model.payment_method)
            .first()
        )

    def get_by_payment_method_and_shop_id(
            self,
            db: Session,
            *,
            shop_id: int,
            payment_method_id: int
    ) -> Optional[models.shop.ShopShopPaymentMethod]:
        return (
            db.query(self.model)
            .filter(self.model.id == shop_id)
            .filter(self.model.payment_method_id == payment_method_id)
            .join(self.model.payment_method)
            .join(self.model.shop)
            .first()
        )


shop_payment_method = ShopPaymentMethodServices(
    models.shop.ShopShopPaymentMethod)
