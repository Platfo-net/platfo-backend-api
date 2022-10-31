import math
from typing import List, Optional
from pydantic import UUID4
from app import models, schemas, services
from sqlalchemy.orm import Session
from app.constants.campaign_status import CampaignStatus


class GroupServices:
    def __init__(self, model):
        self.model = model

    def get_multi(
        self,
        db: Session,
        *,
        facebook_page_id: str,
        user_id: UUID4,
        page: int = 1,
        page_size: int = 20
    ):
        groups = (
            db.query(self.model)
            .filter(
                self.model.facebook_page_id == facebook_page_id,
                self.model.user_id == user_id
            )
            .offset(page_size * (page - 1))
            .limit(page_size)
            .all()
        )

        total_count = db.query(self.model).filter(
            self.model.facebook_page_id == facebook_page_id
        ).count()

        total_page = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_page,
            total_count=total_count,
        )
        return pagination, groups

    def create(self, db: Session, *, obj_in: schemas.postman.GroupCreate, user_id: UUID4):
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            facebook_page_id=obj_in.facebook_page_id,
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: models.postman.Group, obj_in: schemas.postman.GroupUpdate):
        db_obj.name = obj_in.name
        db_obj.description = obj_in.description
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: UUID4):
        return db.query(self.model).filter(self.model.id == id).first()

    def remove(self, db: Session, id: UUID4):
        db_obj = self.get(db, id)
        db.remove(db_obj)
        db.commit()
        return


group = GroupServices(models.postman.Group)
