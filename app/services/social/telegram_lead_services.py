
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class TelegramLeadServices:
    def __init__(self, model):
        self.model: models.social.TelegramLead = model

    def create(self, db: Session, *, obj_in: schemas.social.TelegramLeadCreate):
        db_obj = self.model(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            username=obj_in.username,
            chat_id=obj_in.chat_id,
            telegram_bot_id=obj_in.telegram_bot_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> models.social.TelegramLead:
        return (
            db.query(self.model)
            .join(self.model.telegram_bot)
            .filter(self.model.uuid == uuid)
            .first()
        )

    def get(self, db: Session, *, id: int) -> models.social.TelegramLead:
        return (
            db.query(self.model)
            .join(self.model.telegram_bot)
            .filter(self.model.id == id)
            .first()
        )

    def get_by_chat_id(self, db: Session, *, chat_id: int) -> models.social.TelegramLead:
        return (
            db.query(self.model)
            .join(self.model.telegram_bot)
            .filter(self.model.chat_id == chat_id)
            .first()
        )


telegram_lead = TelegramLeadServices(models.social.TelegramLead)
