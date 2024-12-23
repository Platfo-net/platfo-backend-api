from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.core.unit_of_work import UnitOfWork
from app.core.utils import paginate
from app.schemas.pagination import Pagination


class OrderServices:
    def __init__(self, model):
        self.model: models.shop.ShopOrder = model

    def create(
        self,
        uow: UnitOfWork,
        *,
        obj_in: schemas.shop.OrderCreate,
        shop_id: int,
        lead_id: int,
        shipment_method: models.shop.ShopShipmentMethod,
        shop_payment_method_id: int,
        order_number: int,
        status: str,
        table_id: Optional[int] = None

    ) -> models.shop.ShopOrder:
        db_obj = self.model(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone_number=obj_in.phone_number,
            state=obj_in.state,
            status=status,
            city=obj_in.city,
            address=obj_in.address,
            postal_code=obj_in.postal_code,
            email=obj_in.email,
            order_number=order_number,
            shop_id=shop_id,
            lead_id=lead_id,
            shop_payment_method_id=shop_payment_method_id,
            shipment_method_id=shipment_method.id,
            table_id=table_id,
            shipment_cost_amount=None if not shipment_method else shipment_method.price,
            shipment_cost_currency=None if not shipment_method else shipment_method.currency,
        )

        uow.add(db_obj)
        return db_obj

    def get_last_order_number(self, db: Session, *, shop_id: int) -> int:
        last_order = db.query(self.model).filter(self.model.shop_id == shop_id).order_by(
            desc(self.model.order_number)).first()
        if not last_order:
            return 1000
        return last_order.order_number

    def get(self, db: Session, *, id: int) -> models.shop.ShopOrder:
        return (
            db.query(self.model)
            .join(self.model.items, isouter=True)
            .filter(self.model.id == id)
            .first()
        )

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> models.shop.ShopOrder:
        return (
            db.query(self.model)
            .join(self.model.items)
            .join(self.model.table, isouter=True)
            .join(models.shop.ShopProduct)
            .filter(self.model.uuid == uuid)
            .first()
        )

    def get_shop_orders(
        self, db: Session, *, shop_id: int, status: List[str] = []
    ):
        query = db.query(self.model).join(self.model.table,
                                          isouter=True).filter(self.model.shop_id == shop_id)
        if status:
            query = query.filter(self.model.status.in_(status))
        return query.all()

    def change_status(
        self, db: Session, *, order: models.shop.ShopOrder, status: str
    ):
        order.status = status
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def get_by_order_number_and_shop_id(
        self, db: Session, *, order_number: int, shop_id: int
    ) -> models.shop.ShopOrder:
        return (
            db.query(self.model)
            .join(self.model.lead, isouter=True)
            .filter(self.model.order_number == order_number)
            .filter(self.model.shop_id == shop_id)
            .first()
        )

    def add_payment_image(
        self, db: Session, *, db_obj: models.shop.ShopOrder, image_name: str
    ) -> models.shop.ShopOrder:

        db_obj.payment_image = image_name
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_payment_information(
        self, db: Session, *, db_obj: models.shop.ShopOrder, information: dict
    ) -> models.shop.ShopOrder:
        db_obj.payment_information = information
        db_obj.paid_at = datetime.utcnow()
        db_obj.is_paid = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_shop_id(
        self, db: Session, *, shop_id: int, page: int, page_size: int
    ) -> Tuple[List[models.shop.ShopOrder], Pagination]:
        items = (db.query(self.model)
                 .filter(self.model.shop_id == shop_id)
                 .join(self.model.shop_payment_method, isouter=True)
                 .join(self.model.shipment_method, isouter=True)
                 .join(self.model.table, isouter=True)
                 .order_by(desc(self.model.created_at))
                 .offset(page_size * (page - 1))
                 .limit(page_size)
                 .options(joinedload(self.model.items))
                 .all())

        total_count = db.query(self.model).filter(
            self.model.shop_id == shop_id).count()

        pagination = paginate(total_count, page, page_size)

        return items, pagination

    def has_order_with_table(
        self, db: Session, *, table_id: int
    ) -> bool:
        total_count = db.query(self.model).filter(
            self.model.table_id == table_id).count()

        return bool(total_count)

    def delete(
        self, db: Session, *, db_obj: models.shop.ShopOrder
    ):
        db.delete(db_obj)
        db.commit()

    def get_orders_by_datetime(
        self, db: Session, *, shop_id: int, from_datetime: datetime, to_datetime: datetime
    ) -> List[models.shop.ShopOrder]:
        return db.query(self.model).filter(
            self.model.shop_id == shop_id,
            self.model.created_at >= from_datetime,
            self.model.created_at < to_datetime,
        ).all()

    def update_total_amount(
        self, db: Session, *,
        db_obj: models.shop.ShopOrder,
        total_amount: float,
        currency: str,
    ) -> List[models.shop.ShopOrder]:
        db_obj.total_amount = total_amount
        db_obj.currency = currency
        db.add(db_obj)
        db.commit()


order = OrderServices(models.shop.ShopOrder)
