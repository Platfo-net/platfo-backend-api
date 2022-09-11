import math
from typing import List

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from app import models, schemas
from app.services.base import BaseServices


class ContentServices(
    BaseServices
    [
        models.academy.Content,
        schemas.academy.ContentCreate,
        schemas.academy.ContentUpdate
    ]
):
    def get_multi(
            self,
            db: Session,
            *,
            page: int = 1,
            page_size: int = 20
    ):

        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count
        )
        contents = db.query(self.model).order_by(
            desc(self.model.created_at)
        ) .options(
            joinedload(self.model.content_categories)
        ).offset(page_size * (page - 1)).limit(page_size).all()

        return contents, pagination

    def get_by_detail(
            self,
            db: Session,
            *,
            id: str,
            page: int = 1,
            page_size: int = 20
    ):

        content = db.query(self.model).options(
            joinedload(self.model.content_categories)
        ).filter(self.model.id == id).offset(
            page_size * (page - 1)
        ).limit(page_size).first()

        content_categories = content.content_categories

        categories = []
        for content_category in content_categories:
            categories.append(db.query(
                models.academy.Category
            ).filter(
                models.academy.Category.id == content_category.category_id
            ).first()
            )

        return content, categories

    def search(self,
               db: Session,
               *,
               categories_list: List,
               page: int = 1,
               page_size: int = 20
               ):
        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count
        )
        try:
            contents = []
            for category in categories_list:
                contents.append(
                    db.query(
                        models.academy.Content
                    ).filter(
                        models.academy.Content.content_categories.any(
                            category_id=category
                        )).offset(
                        page_size * (page - 1)
                    ).limit(page_size).all())
            return contents, pagination
        except (Exception,):
            pass

    def create(
            self,
            db: Session,
            *,
            obj_in: schemas.academy.ContentCreate,
    ):
        db_obj = self.model(
            title=obj_in.title,
            detail=obj_in.detail,
            caption=obj_in.caption
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self, db: Session, *,
            db_obj: models.academy.Content,
            obj_in: schemas.academy.ContentCreate
    ):
        db_obj.title = obj_in.title
        db_obj.detail = obj_in.detail
        db_obj.caption = obj_in.caption

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


content = ContentServices(models.academy.Content)
