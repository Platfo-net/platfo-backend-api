from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.unit_of_work import UnitOfWork
from app.core.utils import paginate


class ProductServices:
    def __init__(self, model):
        self.model: models.shop.ShopProduct = model

    def create(
        self,
        uow: UnitOfWork,
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
        uow.add(db_obj)
        return db_obj

    def update(
        self,
        uow: UnitOfWork,
        *,
        db_obj: models.shop.ShopProduct,
        obj_in: schemas.shop.ProductUpdate,
        category_id: Optional[int],
    ) -> models.shop.ShopProduct:
        db_obj.title = obj_in.title
        db_obj.image = obj_in.image
        db_obj.price = obj_in.price,
        db_obj.currency = obj_in.currency,
        db_obj.category_id = category_id,

        uow.add(db_obj)
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
            .filter(self.model.uuid == uuid, self.model.is_deleted == False)  # noqa
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
            .filter(self.model.id == id, self.model.is_deleted == False)  # noqa
            .first()
        )

    def get_multi_by_shop_id(
        self,
        db: Session,
        *,
        shop_id: int,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[models.shop.ShopProduct], schemas.Pagination]:
        conditions = [
            self.model.shop_id == shop_id, self.model.is_deleted == False  # noqa
        ]
        if is_active is not None:
            conditions.append(self.model.is_active == is_active)
        if category_id is not None:
            conditions.append(self.model.category_id == category_id)
        
        q = (
            db.query(self.model)
            .filter(*conditions)
            .join(self.model.category, isouter=True)
            .join(self.model.attributes, isouter=True)
            .join(self.model.variants, isouter=True)
            .order_by(desc(self.model.created_at))
            
        )

        total_count = q.count()

        pagination = paginate(total_count, page, page_size)

        return q.offset(page_size * (page - 1)).limit(page_size).all(), pagination

    def has_with_category(self, db: Session, *, category_id: int):
        return db.query(self.model).filter(
            self.model.category_id == category_id).first() is not None

    def soft_delete(self, uow: UnitOfWork, *, db_obj: models.shop.ShopProduct):
        db_obj.is_deleted = True
        uow.add(db_obj)

    def hard_delete(self, uow: UnitOfWork, *, db_obj: models.shop.ShopProduct):
        uow.delete(db_obj)


product = ProductServices(models.shop.ShopProduct)
