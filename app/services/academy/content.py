
import math
from typing import List
from app.services.base import BaseServices
from sqlalchemy.orm import Session
from app import models, schemas
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4


class ContentServices(
    BaseServices
    [
        models.academy.Content,
        schemas.academy.ContentCreate,
        schemas.academy.ContentUpdate
    ]
):
    def get_multi(self, db: Session, *, page: int = 1, page_size: int = 20):

        contents = db.query(self.model).offset(
            page_size * (page - 1)).limit(page_size).all()
        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count/page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count
        )

        return contents, pagination

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.academy.ContentCreate,
    ):
        db_obj = self.model(
            title=obj_in.title,
            detail=obj_in.detail
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


content = ContentServices(models.academy.Content)
