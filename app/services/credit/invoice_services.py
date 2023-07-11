import math
from typing import Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class InvoiceServices:
    def __init__(self, model):
        self.model: models.credit.Invoice = model

    def get(self, db: Session, id: int) -> Optional[models.credit.Invoice]:
        return (
            db.query(self.model)
            .join(self.model.features)
            .filter(self.model.id == id)
            .first()
        )

    def get_by_uuid(
            self,
            db: Session,
            *,
            uuid: UUID4,
            user_id: int
    ) -> Optional[models.credit.Invoice]:
        return (
            db.query(self.model)
            .join(self.model.features)
            .filter(self.model.uuid == uuid, self.model.user_id == user_id)
            .first()
        )

    def get_multi(self, db: Session, *, currency: str, module: str = None):
        if not module:
            return db.query(self.model).all()
        return (
            db.query(self.model)
            .filter(
                self.model.module == module,
                self.model.currency == currency,
            )
            .all()
        )

    def create(
        self, db: Session, *, obj_in: schemas.credit.InvoiceCreate
    ) -> models.credit.Invoice:
        db_obj = self.model(
            user_id=obj_in.user_id,
            plan_id=obj_in.plan_id,
            amount=obj_in.amount,
            currency=obj_in.currency,
            bought_on_discount=obj_in.bought_on_discount,
            plan_name=obj_in.plan_name,
            module=obj_in.module,
            extend_days=obj_in.extend_days,
            extend_count=obj_in.extend_count,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> None:
        db_obj = self.get(db, id=id)
        db.delete(db_obj)
        db.commit()
        return

    def get_multi_by_user(
        self, db: Session, *, user_id: int, page: int = 1, page_size: int = 20
    ):
        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count,
        )
        offset = (page - 1) * page_size
        invoices = (
            db.query(self.model)
            .filter(user_id == user_id)
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return invoices, pagination


invoice = InvoiceServices(models.credit.Invoice)
