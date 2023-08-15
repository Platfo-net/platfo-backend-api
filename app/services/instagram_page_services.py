from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.models import InstagramPage
from app.services.base import BaseServices


class InstagramPageServices(
    BaseServices[
        models.InstagramPage, schemas.InstagramPageCreate, schemas.InstagramPageUpdate
    ]
):
    def get_multi_by_user_id(self, db: Session, *, user_id: int) -> List[InstagramPage]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_by_instagram_page_id(
        self, db: Session, *, instagram_page_id: int = None
    ) -> models.InstagramPage:
        return (
            db.query(self.model)
            .filter(self.model.instagram_page_id == instagram_page_id)
            .first()
        )

    def delete_by_facebook_page_id(self, db: Session, *, ig_id: int):
        return (
            db.query(self.model).filter(self.model.instagram_page_id == ig_id).delete()
        )

    def get_by_facebook_page_id(
        self, db: Session, *, facebook_page_id: int
    ) -> Optional[models.InstagramPage]:
        return (
            db.query(self.model)
            .filter(self.model.facebook_page_id == facebook_page_id)
            .first()
        )

    def get_page_by_ig_id(
        self, db: Session, *, instagram_page_id: int
    ) -> Optional[models.InstagramPage]:
        return (
            db.query(self.model)
            .filter(self.model.instagram_page_id == instagram_page_id)
            .first()
        )

    def remove(self, db: Session, *, id: int):
        db.query(self.model).filter(self.model.id == id).delete()

    def update_comment_count(self, db: Session, *, facebook_page_id: int, count: int = 1):
        db.query(self.model).filter(
            self.model.facebook_page_id == facebook_page_id
        ).update({'comments_count': self.model.comments_count + count})
        db.commit()

    def update_live_comment_count(self, db: Session, *, facebook_page_id: int, count: int = 1):
        db.query(self.model).filter(
            self.model.facebook_page_id == facebook_page_id
        ).update({'live_comment_count': self.model.live_comment_count + count})
        db.commit()

    def update_leads_count(self, db: Session, *, facebook_page_id: int, count: int = 1):
        db.query(self.model).filter(
            self.model.facebook_page_id == facebook_page_id
        ).update({'leads_count': self.model.leads_count + count})
        db.commit()

    def update_chats_count(self, db: Session, *, facebook_page_id: int, count: int = 1):
        db.query(self.model).filter(
            self.model.facebook_page_id == facebook_page_id
        ).update({'chats_count': self.model.chats_count + count})
        db.commit()


instagram_page = InstagramPageServices(models.InstagramPage)
