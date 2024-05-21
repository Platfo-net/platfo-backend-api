from typing import List

from sqlalchemy.orm import Session

from app import models, schemas
from app.core.unit_of_work import UnitOfWork


class OrderItemServices:

    def __init__(self, model):
        self.model: models.shop.ShopOrderItem = model

    def create_bulk(self, uow: UnitOfWork, objs_in: List[schemas.shop.OrderItem],
                    order_id: int) -> List[models.shop.ShopOrderItem]:
        db_objs = []
        for obj in objs_in:
            db_objs.append(
                self.model(
                    product_id=obj.product_id,
                    count=obj.count,
                    order_id=order_id,
                    price=obj.price,
                    currency=obj.currency,
                    product_title=obj.product_title,
                    variant_title=obj.variant_title,
                ))
        uow.add_all(db_objs)
        return db_objs

    def has_item_with_product_id(self, db: Session, *, product_id: int) -> bool:
        return db.query(self.model).filter(self.model.product_id == product_id).first() is not None


order_item = OrderItemServices(models.shop.ShopOrderItem)
