from typing import Optional

from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import paginate


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
            lead_number=obj_in.lead_number,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> models.social.TelegramLead:
        return (db.query(self.model).join(
            self.model.telegram_bot).filter(self.model.uuid == uuid).first())

    def get(self, db: Session, *, id: int) -> models.social.TelegramLead:
        return (db.query(self.model).join(
            self.model.telegram_bot).filter(self.model.id == id).first())

    def get_by_chat_id(self, db: Session, *, chat_id: int,
                       telegram_bot_id: int) -> models.social.TelegramLead:
        return (db.query(self.model).join(self.model.telegram_bot).filter(
            self.model.chat_id == chat_id, self.model.telegram_bot_id == telegram_bot_id).first())

    def get_last_lead_number(self, db: Session, *, telegram_bot_id: int) -> int:
        lead = db.query(self.model).filter(self.model.telegram_bot_id == telegram_bot_id).order_by(
            desc(self.model.lead_number)).first()
        if not lead:
            return 0
        return lead.lead_number

    def get_by_lead_number_and_telegram_bot_id(
            self, db: Session, *, lead_number: int,
            telegram_bot_id: int) -> Optional[models.social.TelegramLead]:
        return (db.query(self.model).filter(self.model.telegram_bot_id == telegram_bot_id,
                                            self.model.lead_number == lead_number).first())

    def get_multi_by_telegram_bot_id(
        self,
        db: Session,
        *,
        telegram_bot_id: int,
        page: int = 1,
        page_size: int = 20,
    ):
        leads = db.query(self.model).join(self.model.telegram_bot). \
            filter(self.model.telegram_bot_id == telegram_bot_id). \
            offset(page_size * (page - 1)).limit(page_size).all()
        total_count = db.query(
            self.model).filter(self.model.telegram_bot_id == telegram_bot_id).count()
        pagination = paginate(total_count, page, page_size)
        return leads, pagination

    def change_is_ai_answer(self, db: Session, *, db_obj: models.social.TelegramLead,
                            is_ai_answer: bool):
        db_obj.is_ai_answer = is_ai_answer
        db.add(db_obj)
        db.commit()
        db.refresh()


telegram_lead = TelegramLeadServices(models.social.TelegramLead)
