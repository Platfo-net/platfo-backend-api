from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models
from app.constants.message_builder import MessageStatus


class MessageServices:
    def __init__(self, model):
        self.model: models.message_builder.MessageBuilderMessage = model

    def create(self, db: Session, *, chat_id: int):
        db_obj = self.model(
            telegram_chat_id=chat_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh()
        return db_obj

    def get_last_message(self, db: Session, *, chat_id: int, status: str = None):
        q = db.query(self.model).filter(
            self.model.telegram_chat_id == chat_id
        )
        if status:
            q = q.filter(self.model.status == status)

        return q.order_by(desc(self.model.created_at)).first()

    def remove(self, db: Session, *, db_obj):
        db.delete(db_obj)
        db.commit()

    def get(self, db: Session, *, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_chat_id_and_id(self, db: Session, *, id: int, chat_id: int):
        return db.query(self.model).filter(self.model.id == id, self.model.telegram_chat_id == chat_id).first()

    def change_status(self, db: Session, *, db_obj, status):
        db_obj.status = status

        db.add(db_obj)
        db.commit()


message = MessageServices(models.message_builder.MessageBuilderMessage)
