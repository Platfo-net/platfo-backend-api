from pydantic import UUID4
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session


class FacebookAccountServices(
        BaseServices[
            models.FacebookAccount,
            schemas.FacebookAccountCreate,
            schemas.FacebookAccountUpdate
        ]):
    def delete_by_user_id(self, db: Session, *, user_id: UUID4):
        db_obj = db.query(self.model).filter(self.model.user_id == user_id)\
            .first()
        db.delete(db_obj)
        db.commit()
        return db_obj

    def get_by_user_id(self, db: Session, *, user_id: UUID4):
        return db.query(self.model).filter(
            self.model.user_id == user_id
        ).first()

    def get_by_facebook_user_id(self, db: Session, *, facebook_user_id: str):
        return db.query(self.model).filter(
            self.model.facebook_user_id == facebook_user_id
        ).first()


facebook_account = FacebookAccountServices(models.FacebookAccount)
