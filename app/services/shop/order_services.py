from typing import List

from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas
from app.constants.order_status import OrderStatus


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
            .filter(self.model.id == id)
            .first()
        )

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> models.shop.ShopOrder:
        return (
            db.query(self.model)
            .join(self.model.items)
            .filter(self.model.uuid == uuid)
            .first()
        )

    def pay_order(
        self, db: Session, *,
        order: models.shop.ShopOrder,
        payment_info: schemas.shop.OrderAddPaymentInfo
    ):
        order.status = OrderStatus.PAYMENT_CHECK
        order.payment_card_last_four_number = payment_info.payment_reference_number
        order.payment_card_last_four_number = payment_info.payment_card_last_four_number
        order.payment_card_last_four_number = payment_info.payment_datetime
        order.payment_card_last_four_number = payment_info.payment_receipt_image
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def get_shop_orders(
        self, db: Session, *, shop_id: int, status: List[str] = []
    ):
        query = db.query(self.model).filter(self.model.shop_id == shop_id)
        if status:
            query = query.filter(self.model.status.in_(status))
        return query.all()


order = OrderServices(models.shop.ShopOrder)
