from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app import models, schemas


class MessageServices:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, *, obj_in: schemas.live_chat.MessageCreate):
        if isinstance(obj_in.content,  str):
            obj_in.content = {'text': obj_in.content}

        message = self.model(
            from_page_id=obj_in.from_page_id,
            to_page_id=obj_in.to_page_id,
            content=obj_in.content,
            mid=obj_in.mid,
            user_id=obj_in.user_id,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_page_messages(
        self,
        db: Session,
        *,
        lead_igs_id: str,
        page_id: str,
        skip: int = 0,
        limit: int = 20
    ):
        return (
            db.query(self.model)
            .filter(
                or_(
                    and_(
                        self.model.from_page_id == lead_igs_id,
                        self.model.to_page_id == page_id,
                    ),
                    and_(
                        self.model.from_page_id == page_id,
                        self.model.to_page_id == lead_igs_id,
                    ),
                )
            )
            .order_by(self.model.send_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def remove_by_user_page_id(self, db: Session, *, user_page_id: str):
        messages = (
            db.query(self.model)
            .filter(
                or_(
                    self.model.from_page_id == user_page_id,
                    self.model.to_page_id == user_page_id,
                )
            )
            .all()
        )

        for message in messages:
            db.delete(message)

        db.commit()
        return

    def remove_message_by_mid(self, db: Session, *, mid: str):
        message = db.query(self.model).filter(self.model.mid == mid).first()
        db.delete(message)
        db.commit()
        # db.refresh(message)
        return


message = MessageServices(models.live_chat.Message)
