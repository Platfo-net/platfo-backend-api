from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class PaymentMethodServices:
    def __init__(self, model):
        self.model: models.shop.ShopPaymentMethod = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.PaymentMethodCreate,
        shop_id: int,
    ) -> models.shop.ShopPaymentMethod:
        db_obj = self.model(
            title=obj_in.title,
            shop_id=shop_id,
            description=obj_in.description,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopPaymentMethod,
        obj_in: schemas.shop.PaymentMethodCreate,
    ) -> models.shop.ShopPaymentMethod:
        db_obj.title = obj_in.title
        db_obj.description = obj_in.description,

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

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

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int
    ) -> List[models.shop.ShopPaymentMethod]:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.shop.user_id == user_id)
            .all()
        )

    def get_multi_by_shop_id(
        self,
        db: Session,
        *,
        shop_id: int,
        is_active: Optional[bool] = None
    ) -> List[models.shop.ShopPaymentMethod]:
        items = (
            db.query(self.model)
            .filter(self.model.shop_id == shop_id)
        )
        if is_active is not None:
            items = items.filter(self.model.is_active == is_active)
        return items.all()

    def delete(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopPaymentMethod
    ):
        db.delete(db_obj)
        db.commit()


payment_method = PaymentMethodServices(models.shop.ShopPaymentMethod)
