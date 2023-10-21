from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.unit_of_work import UnitOfWork


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


shop_payment_method = ShopPaymentMethodServices(models.shop.ShopShopPaymentMethod)
