
from pydantic import UUID4
from app import models, schemas
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder


class ContentAttachmentServices:
    def __init__(self, model):
        self.model = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.academy.ContentAttachmentCreate,
        content_id: UUID4
    ):
        db_obj = self.model(**jsonable_encoder(obj_in),
                            content_id=content_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def get_by_content_id(
            self,
            db: Session,
            *,
            content_id: UUID4
    ):
        return db.query(self.model).filter(
            self.model.content_id == content_id
        )

    def remove_by_content_id(
            self,
            db: Session,
            *,
            content_id: UUID4
    ):
        return db.query(self.model).filter(
            self.model.content_id == content_id
        ).delete()


content_attachment = ContentAttachmentServices(
    models.academy.ContentAttachment)
