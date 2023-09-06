
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class TelegramLeadServices:
    def __init__(self, model):
        self.model: models.live_chat.TelegramLead = model

    def create(self, db: Session, *, obj_in: schemas.lead.TelegramLeadCreate):
        db_obj = self.model(
            chat_id=obj_in.chat_id,
            telegram_bot_id=obj_in.telegram_bot_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> models.lead.TelegramLead:
        return (
            db.query(self.model)
            .join(self.model.telegram_bot)
            .filter(self.model.uuid == uuid)
            .first()
        )


telegram_lead = TelegramLeadServices(models.lead.TelegramLead)
