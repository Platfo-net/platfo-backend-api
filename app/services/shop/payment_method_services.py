from typing import List
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
    ) -> models.shop.ShopPaymentMethod:
        db_obj = self.model(
            title=obj_in.title,
            description=obj_in.description,
            information_fields=obj_in.information_fields,
            payment_fields=obj_in.payment_fields,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_title(
        self,
        db: Session,
        *,
        title: str
    ) -> models.shop.ShopPaymentMethod:
        return db.query(self.model).filter(self.model.title == title).first()

    def all(
        self,
        db: Session,
    ) -> List[models.shop.ShopPaymentMethod]:
        return db.query(self.model).all()


payment_method = PaymentMethodServices(models.shop.ShopPaymentMethod)
