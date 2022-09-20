from pydantic import UUID4
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session


class InstagramPageServices(
        BaseServices[
            models.InstagramPage,
            schemas.InstagramPageCreate,
            schemas.InstagramPageUpdate
        ]):
    def get_multi_by_user_id(self, db: Session, *, user_id: UUID4)-> models.InstagramPage:
        return db.query(self.model).filter(
            self.model.user_id == user_id
        ).all()

    def get_by_instagram_page_id(
        self, db: Session, *, instagram_page_id: str = None
    ) -> models.InstagramPage:
        return db.query(self.model).filter(
            self.model.instagram_page_id == instagram_page_id
        ).first()

    def delete_by_facebook_page_id(self, db: Session, *, ig_id):
        return db.query(self.model).filter(
            self.model.instagram_page_id == ig_id
        ).delete()

    def get_by_facebook_page_id(self, db: Session, *, facebook_page_id: str):
        return db.query(self.model)\
            .filter(self.model.facebook_page_id == facebook_page_id).first()


instagram_page = InstagramPageServices(models.InstagramPage)
