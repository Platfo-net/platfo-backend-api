
import math
from typing import List
from app.services.base import BaseServices
from sqlalchemy.orm import Session
from app import models, schemas
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4


class CategoryServices(
    BaseServices
    [
        models.academy.Category,
        schemas.academy.CategoryCreate,
        schemas.academy.CategoryUpdate
    ]
):
    def get_multi(db: Session, *, page: int = 1, page_size: int = 20):

        items = db.query(models.Category).offset(
            page_size * (page - 1)).limit(page_size).all()
        total_count = db.query(models.Category).count()
        total_pages = math.ceil(total_count / page_size)

        return items


category = CategoryServices(models.academy.Category)
