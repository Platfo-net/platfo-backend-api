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
    def delete_by_facebook_account_id(self, db: Session, *, account_id: UUID4):
        return db.query(self.model).filter(
            self.model.facebook_account_id == account_id
        ).delete()

    def get_multi_by_user_id(self, db: Session, *, user_id: UUID4):
        account = db.query(models.FacebookAccount).filter(
            models.FacebookAccount.user_id == user_id).first()

        if not account:
            return []
        pages = db.query(self.model).filter(
            self.model.facebook_account_id == account.id
        ).all()
        return pages

    def get_page_by_instagram_page_id(
        self, db: Session, *, instagram_page_id: str = None
    ) -> schemas.InstagramPage:
        return db.query(self.model).filter(
            self.model.instagram_page_id == instagram_page_id
        ).first()

    def delete_by_page_id(self, db: Session, *, ig_id):
        return db.query(self.model).filter(
            self.model.instagram_page_id == ig_id
        ).delete()

    def get_by_page_id(self, db: Session, *, page_id: str):
        return db.query(self.model)\
            .filter(self.model.facebook_page_id == page_id).first()


instagram_page = InstagramPageServices(models.InstagramPage)
