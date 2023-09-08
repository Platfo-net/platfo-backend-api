from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas


class OrderServices:
    def __init__(self, model):
        self.model: models.shop.ShopOrder = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.OrderCreate,
        shop_id: int,
        lead_id: int,
        order_number: int,
        status: str,
    ) -> models.shop.ShopOrder:
        db_obj = self.model(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone_number=obj_in.phone_number,
            state=obj_in.state,
            city=obj_in.city,
            address=obj_in.address,
            postal_code=obj_in.postal_code,
            email=obj_in.email,
            order_number=order_number,
            shop_id=shop_id,
            lead_id=lead_id,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_last_order_number(self, db: Session, *, shop_id: int) -> int:
        last_order = db.query(self.model).filter(self.model.shop_id == shop_id).order_by(
            desc(self.model.order_number)).first()
        if not last_order:
            return 10000000
        return last_order.order_number

    def get(self, db: Session, *, id: int) -> models.shop.ShopOrder:
        return (
            db.query(self.model)
            .join(self.model.items)
            .join(self.model.items.product)
            .filter(self.model.id == id)
            .first()
        )


order = OrderServices(models.shop.ShopOrder)
