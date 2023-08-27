from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas


class TelegramBotServices:
    def __init__(self, model):
        self.model: models.TelegramBot = model

    def get_by_id(self, db: Session, *, bot_id: str) -> Optional[models.TelegramBot]:
        return db.query(self.model).filter(self.model.bot_id == bot_id).first()

    def create(
            self,
            db: Session,
            *,
            obj_in: schemas.TelegramBotCreate,
            user_id: int
    ) -> models.TelegramBot:
        db_obj = self.model(
            bot_id=obj_in.bot_id,
            username=obj_in.username,
            app_id=obj_in.app_id,
            app_secret=obj_in.app_secret,
            bot_token=obj_in.bot_token,
            first_name=obj_in.first_name,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


telegram_bot = TelegramBotServices(models.TelegramBot)
