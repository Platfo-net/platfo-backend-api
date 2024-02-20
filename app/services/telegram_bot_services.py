from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas


class TelegramBotServices:
    def __init__(self, model):
        self.model: models.TelegramBot = model

    def get_by_uuid(self, db: Session, *, uuid: UUID4) -> Optional[models.TelegramBot]:
        return db.query(self.model).filter(self.model.uuid == uuid).first()

    def get_by_bot_id(self, db: Session, *, bot_id: int) -> Optional[models.TelegramBot]:
        return db.query(self.model).filter(self.model.bot_id == bot_id).first()

    def get_by_bot_token(self, db: Session, *, token: str) -> Optional[models.TelegramBot]:
        return db.query(self.model).filter(self.model.bot_token == token).first()

    def get_multi_by_user_id(self, db: Session, *, user_id: str) -> List[models.TelegramBot]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

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
            bot_token=obj_in.bot_token,
            first_name=obj_in.first_name,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: models.TelegramBot,
        obj_in: schemas.TelegramBotUpdate,
    ) -> models.TelegramBot:
        db_obj.welcome_message = obj_in.welcome_message
        db_obj.button_name = obj_in.button_name
        db_obj.app_link = obj_in.app_link
        db_obj.image = obj_in.image
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(
            self,
            db: Session,
            *,
            id: int
    ) -> models.TelegramBot:
        return db.query(self.model).filter(self.model.id == id).first()

    def all(
            self,
            db: Session,
    ) -> List[models.TelegramBot]:
        return db.query(self.model).all()


telegram_bot = TelegramBotServices(models.TelegramBot)
