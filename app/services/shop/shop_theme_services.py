from sqlalchemy.orm import Session

from app import models, schemas


class ShopThemeServices:
    def __init__(self, model):
        self.model: models.shop.ShopTheme = model

    def create(
            self,
            db: Session,
            *,
            obj_in: schemas.shop.ShopUpdate,
            shop_id: int,

    ) -> models.shop.ShopTheme:
        db_obj = self.model(
            color_code=obj_in.color_code,
            shop_id=shop_id
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj: models.shop.ShopTheme,
            obj_in: schemas.shop.ShopUpdate,

    ) -> models.shop.ShopTheme:
        db_obj.color_code = obj_in.color_code

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_shop_id(self, db: Session, *, shop_id: int) -> models.shop.ShopTheme:
        return (
            db.query(self.model).filter(self.model.shop_id == shop_id).first()
        )


shop_theme = ShopThemeServices(models.shop.ShopTheme)
