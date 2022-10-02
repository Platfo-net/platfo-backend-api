
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models


class LabelContentServices:

    def __init__(self, model):
        self.model = model

    def create(
            self,
            db: Session,
            *,
            label_id: UUID4,
            content_id: UUID4,
    ):
        db_obj = self.model(label_id=label_id,
                            content_id=content_id)
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
        return db.query(self.model).filter(
                self.model.content_id == content_id).\
            delete()


label_content = LabelContentServices(models.academy.ContentLabel)
