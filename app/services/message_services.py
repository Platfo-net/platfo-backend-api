from typing import List
from app import models, schemas
from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_


class MessageServices:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, *, obj_in: schemas.MessageCreate):
        if type(obj_in.content) == str:
            obj_in.content = {
                "text": obj_in.content
            }
        message = self.model(
            from_page_id=obj_in.from_page_id,
            to_page_id=obj_in.to_page_id,
            content=obj_in.content,
            user_id=obj_in.user_id
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_pages_messages(
        self,
        db: Session,
        *,
        contact_igs_id: UUID4,
        page_id: UUID4,
        skip: int = 0,
        limit: int = 20
    ) -> List[schemas.Message]:

        return db.query(self.model).filter(
            or_(
                and_(
                    self.model.from_page_id == contact_igs_id,
                    self.model.to_page_id == page_id
                ),
                and_(
                    self.model.from_page_id == page_id,
                    self.model.to_page_id == contact_igs_id
                ),

            )
        ).order_by(self.model.send_at.desc()).offset(skip).limit(limit).all()


message = MessageServices(models.Message)
