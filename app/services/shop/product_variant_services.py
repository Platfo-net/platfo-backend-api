from typing import List, Optional
from sqlalchemy import delete
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class VariantServices:
    def __init__(self, model):
        self.model: models.shop.ShopProductVariant = model

    def create_bulk(
        self,
        db: Session,
        *,
        variants: List[schemas.shop.VariantCreate],
        product_id: int
    ) -> List[models.shop.ShopProductVariant]:
        items = [
            self.model(
                title=variant.title,
                price=variant.price,
                currency=variant.currency,
                product_id=product_id,
                is_available=variant.is_available,
            )
            for variant in variants
        ]
        db.add_all(items)
        db.commit()
        return items

    def delete_by_product_id(
        self,
        db: Session,
        *,
        product_id: int
    ) -> List[models.shop.ShopProductVariant]:
        q = delete(self.model).where(self.model.product_id == product_id)
        db.execute(q)

    def get_by_uuid(
        self,
        db: Session,
        *,
        uuid: UUID4
    ) -> Optional[models.shop.ShopProductVariant]:
        return db.query(self.model).filter(self.model.uuid == uuid).first()


product_variant = VariantServices(models.shop.ShopProductVariant)
