from typing import List

from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import paginate


class ProductServices:
    def __init__(self, model):
        self.model: models.shop.ShopProduct = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.shop.ProductCreate,
        shop_id: int,
        category_id: int,
    ) -> models.shop.ShopProduct:
        db_obj = self.model(
            title=obj_in.title,
            image=obj_in.image,
            price=obj_in.price,
            currency=obj_in.currency,
            category_id=category_id,
            shop_id=shop_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: models.shop.ShopProduct,
        obj_in: schemas.shop.ProductUpdate,
    ) -> models.shop.ShopProduct:
        db_obj.title = obj_in.title
        db_obj.image = obj_in.image
        db_obj.price = obj_in.price,
        db_obj.currency = obj_in.currency,
        db_obj.category_id = obj_in.category_id,

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4
    ) -> models.shop.ShopProduct:
        return (
            db.query(self.model)
            .join(self.model.category, isouter=True)
            .filter(self.model.uuid == uuid)
            .first()
        )

    def get(
        self,
        db: Session,
        *,
        id: int
    ) -> models.shop.ShopProduct:
        return (
            db.query(self.model)
            .join(self.model.category, isouter=True)
            .filter(self.model.id == id)
            .first()
        )

    def get_multi_by_shop_id(
        self,
        db: Session,
        *,
        shop_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[models.shop.ShopProduct], schemas.Pagination]:
        items = (db.query(self.model)
                 .filter(self.model.shop_id == shop_id)
                 .join(self.model.category, isouter=True)
                 .order_by(desc(self.model.created_at))
                 .offset(page_size * (page - 1))
                 .limit(page_size)
                 .all())

        total_count = db.query(self.model).filter(
            self.model.shop_id == shop_id).count()

        pagination = paginate(total_count, page, page_size)

        return items, pagination

    def delete(self, db: Session, *, db_obj: models.shop.ShopProduct):
        db.delete(db_obj)
        db.commit()


product = ProductServices(models.shop.ShopProduct)
