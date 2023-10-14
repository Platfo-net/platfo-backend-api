from typing import List

from sqlalchemy.orm import Session

from app import models, schemas


class OrderItemServices:
    def __init__(self, model):
        self.model: models.shop.ShopOrderItem = model

    def create_bulk(
        self,
        db: Session,
        objs_in: List[schemas.shop.OrderItemCreate],
        order_id: int
    ) -> List[models.shop.ShopOrderItem]:
        db_objs = []
        for obj in objs_in:
            db_objs.append(self.model(
                product_id=obj.product_id,
                count=obj.count,
                order_id=order_id,
                price=obj.price,
                currency=obj.currency,
            ))
        db.add_all(db_objs)
        db.commit()
        return db_objs

    def set_product_title_after_delete_product(
        self,
        db: Session,
        *,
        product_id: int,
        product_title: str,
    ):
        (db.query(self.model)
         .filter(self.model.product_id == product_id)
         .update({"product_title": product_title}))
        db.commit()


order_item = OrderItemServices(models.shop.ShopOrderItem)
