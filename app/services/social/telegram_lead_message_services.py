from sqlalchemy.orm import Session

from app import models, schemas


class TelegramLeadMessageServices:
    def __init__(self, model):
        self.model: models.social.TelegramLeadMessage = model

    def create(self, db: Session, *, obj_in: schemas.social.TelegramLeadMessageCreate
               ) -> models.social.TelegramLeadMessage:
        db_obj = self.model(
            lead_id=obj_in.lead_id,
            is_lead_to_bot=obj_in.is_lead_to_bot,
            message=obj_in.message,
            message_id=obj_in.message_id,
            mirror_message_id=obj_in.mirror_message_id,
            reply_to_id=obj_in.reply_to_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


telegram_lead_message = TelegramLeadMessageServices(models.social.TelegramLeadMessage)
