
import math

from sqlalchemy.orm import Session

from app import models, schemas
from app.services.base import BaseServices


class CategoryServices(
    BaseServices
    [
        models.academy.Category,
        schemas.academy.CategoryCreate,
        schemas.academy.CategoryUpdate
    ]
):
    def get_multi(
            self,
            db: Session,
            *,
            page: int = 1,
            page_size: int = 20
    ):
        categories = db.query(self.model).offset(
            page_size * (page - 1)).limit(page_size).all()

        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count
        )

        return categories, pagination

    def create(
            self,
            db: Session,
            *,
            obj_in: schemas.academy.CategoryCreate,
    ):
        db_obj = self.model(
            title=obj_in.title,
            parent_id=obj_in.parent_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


category = CategoryServices(models.academy.Category)
