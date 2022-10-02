
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models


class CategoryContentServices:

    def __init__(self, model):
        self.model = model

    def create(self,
               db: Session,
               *,
               category_id: UUID4,
               content_id: UUID4,
               ):
        db_obj = self.model(category_id=category_id, content_id=content_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return

    def remove_by_content_id(
            self,
            db: Session,
            *,
            content_id: UUID4
    ):
        return db.query(self.model).filter(self.model.
                                           content_id == content_id).delete()


category_content = CategoryContentServices(models.academy.ContentCategory)
