from typing import List

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.unit_of_work import UnitOfWork


class CategoryServices:
    def __init__(self, model):
        self.model: models.shop.ShopCategory = model

    def create(
        self,
        uow: UnitOfWork,
        *,
        obj_in: schemas.shop.CategoryCreate,
        shop_id: int,
    ) -> models.shop.ShopCategory:
        db_obj = self.model(
            title=obj_in.title,
            shop_id=shop_id,
            image=obj_in.image,
        )
        uow.add(db_obj)
        return db_obj

    def update(
        self,
        uow: UnitOfWork,
        *,
        db_obj: models.shop.ShopCategory,
        obj_in: schemas.shop.CategoryUpdate,
    ) -> models.shop.ShopCategory:
        db_obj.title = obj_in.title
        db_obj.image = obj_in.image
        uow.add(db_obj)
        return db_obj

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4
    ) -> models.shop.ShopCategory:
        return db.query(self.model).join(self.model.shop).filter(
            self.model.uuid == uuid, self.model.is_deleted == False).first()  # noqa

    def get(
        self,
        db: Session,
        *,
        id: int
    ) -> models.shop.ShopCategory:
        return db.query(self.model).join(self.model.shop).filter(
            self.model.id == id, self.model.is_deleted == False).first()  # noqa

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int
    ) -> List[models.shop.ShopCategory]:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.shop.user_id == user_id)
            .all()
        )

    def get_multi_by_shop(
        self,
        db: Session,
        *,
        shop_id: int
    ) -> List[models.shop.ShopCategory]:
        return (
            db.query(self.model)
            .join(self.model.shop)
            .filter(self.model.shop_id == shop_id, self.model.is_deleted == False)  # noqa
            .all()
        )

    def soft_delete(
        self,
        uow: UnitOfWork,
        *,
        db_obj: models.shop.ShopCategory
    ):
        db_obj.is_deleted = True
        uow.add(db_obj)

    def hard_delete(
        self,
        uow: UnitOfWork,
        *,
        db_obj: models.shop.ShopCategory
    ):
        uow.delete(db_obj)


category = CategoryServices(models.shop.ShopCategory)
