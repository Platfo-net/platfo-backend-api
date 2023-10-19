from typing import List

from app import models, schemas
from app.core.unit_of_work import UnitOfWork


class OrderItemServices:
    def __init__(self, model):
        self.model: models.shop.ShopOrderItem = model

    def create_bulk(
        self,
        uow: UnitOfWork,
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
        uow.add_all(db_objs)
        return db_objs

    def set_product_title_after_delete_product(
        self,
        uow: UnitOfWork,
        *,
        product_id: int,
        product_title: str,
    ):
        (uow.query(self.model)
         .filter(self.model.product_id == product_id)
         .update({"product_title": product_title}))


order_item = OrderItemServices(models.shop.ShopOrderItem)
