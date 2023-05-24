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


instagram_page = InstagramPageServices(models.InstagramPage)
