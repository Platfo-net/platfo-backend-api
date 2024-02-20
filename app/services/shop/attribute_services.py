from typing import List

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app import models, schemas


class AttributeServices:
    def __init__(self, model):
        self.model: models.shop.ShopAttribute = model

    def create_bulk(
            self,
            db: Session,
            objs_in: List[schemas.shop.AttributeCreate],
            product_id: int,
    ) -> List[models.shop.ShopAttribute]:
        if not objs_in:
            return []
        db_objs = []
        for obj in objs_in:
            db_objs.append(self.model(
                product_id=product_id,
                key=obj.key,
                value=obj.value,
            ))
        db.add_all(db_objs)
        db.commit()
        return db_objs

    def delete_by_product_id(
        self, db: Session, *, product_id: int
    ):
        q = delete(self.model).where(self.model.product_id == product_id)
        db.execute(q)

    def delete(
            self,
            db: Session,
            *,
            db_obj: models.shop.ShopAttribute
    ):
        db.delete(db_obj)
        db.commit()


attribute = AttributeServices(models.shop.ShopAttribute)
