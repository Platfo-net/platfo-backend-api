
import math

from sqlalchemy.orm import Session

from app import models, schemas
from app.services.base import BaseServices


class LabelServices(
    BaseServices
    [
        models.academy.Label,
        schemas.academy.LabelCreate,
        schemas.academy.LabelUpdate
    ]
):
    def get_multi(
            self,
            db: Session,
            *,
            page: int = 1,
            page_size: int = 20
    ):
        labels = db.query(self.model).offset(
            page_size * (page - 1)).limit(page_size).all()

        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count
        )
        return labels, pagination

    def create(
            self,
            db: Session,
            *,
            obj_in: schemas.academy.LabelCreate,
    ):
        db_obj = self.model(
            label_name=obj_in.label_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


label = LabelServices(models.academy.Label)
