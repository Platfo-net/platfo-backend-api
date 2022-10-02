
import math
from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

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

        contents = db.query(self.model).order_by(
            desc(self.model.created_at)
        ).options(
            joinedload(self.model.content_categories),
            joinedload(self.model.content_labels)) \
            .offset(page_size * (page - 1)).limit(page_size).all()

        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count
        )
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
            joinedload(self.model.content_categories),
            joinedload(self.model.content_labels)).\
            filter(self.model.id == id).offset(
            page_size * (page - 1)
        ).limit(page_size).first()

        content_categories = content.content_categories
        content_labels = content.content_labels

        categories = []
        for content_category in content_categories:
            categories.append(db.query(
                models.academy.Category
            ).filter(
                models.academy.Category.id == content_category.category_id
            ).first()
               )
        labels = []
        for content_label in content_labels:
            labels.append(db.query(
                models.academy.Label
            ).filter(
                models.academy.Label.id == content_label.label_id
            ).first()
                          )

        return content, categories, labels

    def search(
            self,
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

    def create(  # noqa
            self,
            db: Session,
            *,
            obj_in: schemas.academy.ContentCreate,
            user_id: UUID4
    ):
        sub_data = []
        for item in obj_in.blocks:
            data = None
            if item.type == 'paragraph':
                data = schemas.academy.\
                    SubData(text=item.data.text)
            if item.type == 'header':
                data = schemas.academy.\
                    SubData(text=item.data.text, level=item.data.style)
            if item.type == 'heading':
                data = schemas.academy.\
                    SubData(text=item.data.text, level=item.data.style)
            if item.type == 'list':
                data = schemas.academy.\
                    SubData(style=item.data.style, items=item.data.items)
            if item.type == 'image':
                data = schemas.academy.SubData(
                    file=schemas.academy.File(url=item.data.file.url),
                    caption=item.data.caption,
                    withBorder=item.data.withBorder,
                    stretched=item.data.stretched,
                    withBackground=item.data.withBackground
                )
            sub_data.append(
                schemas.academy.
                Data(id=item.id, type=item.type, data=data)
                        )

        blocks = [
            {
                "id": sub.id,
                "type": sub.type,
                "data": jsonable_encoder(sub.data)
            } for sub in sub_data
        ]

        db_obj = self.model(
            title=obj_in.title,
            blocks=blocks,
            caption=obj_in.caption,
            is_published=obj_in.is_published,
            user_id=user_id,
            cover_image=obj_in.cover_image,
            version=obj_in.version,
            time=obj_in.time
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(  # noqa
            self,
            db: Session,
            *,
            db_obj: models.academy.Content,
            obj_in: schemas.academy.ContentCreate,
            user_id: UUID4
    ):
        db_obj.title = obj_in.title
        db_obj.blocks = jsonable_encoder(obj_in.blocks)
        db_obj.caption = obj_in.caption
        db_obj.user_id = user_id
        db_obj.cover_image = obj_in.cover_image
        db_obj.version = obj_in.version
        db_obj.time = obj_in.time

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


content = ContentServices(models.academy.Content)
