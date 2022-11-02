import math
from typing import List
from pydantic import UUID4
from app import models, schemas, services
from sqlalchemy.orm import Session
from app.constants.campaign_status import CampaignStatus

from sqlalchemy import and_

from fastapi.encoders import jsonable_encoder
ModelType = models.postman.Campaign
CreateSchemaType = schemas.postman.CampaignCreate
UpdateSchemaType = schemas.postman.CampaignUpdate


class CampaignServices:
    def __init__(self, model):
        self.model = model

    def get_multi(
        self,
        db: Session,
        *,
        facebook_page_id: str = None,
        user_id: UUID4,
        page: int = 1,
        page_size: int = 20
    ):
        condition = [self.model.self.model.user_id == user_id]
        if facebook_page_id:
            condition.append(self.model.self.model.facebook_page_id == facebook_page_id)

        campaigns = (
            db.query(self.model)
            .filter(and_(*condition))
            .offset(page_size * (page - 1))
            .limit(page_size)
            .all()
        )

        total_count = db.query(self.model).filter(
            and_(*condition)
        ).count()
        total_page = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_page,
            total_count=total_count,
        )
        return pagination, campaigns

    def create(
            self,
            db: Session,
            *,
            obj_in: CreateSchemaType,
            user_id: UUID4
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        user_id: UUID4,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:

        db_obj.name = obj_in.name
        db_obj.description = obj_in.description
        db_obj.facebook_page_id = obj_in.facebook_page_id
        db_obj.content = obj_in.content
        db_obj.is_draft = obj_in.is_draft
        db_obj.user_id = user_id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_active_campaigns(self, db: Session) -> List[ModelType]:
        return db.query(models.postman.Campaign).filter(
            models.postman.Campaign.is_draft == False,  # noqa
            models.postman.Campaign.status == CampaignStatus.PENDING,
            models.postman.Campaign.is_active == False  # noqa
        ).all()

    def get(
        self,
        db: Session,
        campaign_id: UUID4
    ) -> ModelType:

        return db.query(models.postman.Campaign)\
            .filter(models.postman.Campaign.id == campaign_id).first()

    def change_status(
        self,
        db: Session,
        *,
        campaign_id: UUID4,
        status: str = CampaignStatus.DONE,
    ) -> ModelType:

        campaign = services.postman.campaign.get(db=db, campaign_id=campaign_id)
        campaign.status = status

        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def change_is_draft(
        self,
        db: Session,
        *,
        campaign_id: UUID4,
        is_draft: bool,
    ) -> ModelType:

        campaign = services.postman.campaign.get(db=db, campaign_id=campaign_id)
        campaign.is_draft = is_draft

        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def change_activity(
        self,
        db: Session,
        *,
        campaign_id: UUID4,
        is_active: bool,
    ) -> ModelType:

        campaign = services.postman.campaign.get(db=db, campaign_id=campaign_id)
        campaign.is_active = is_active

        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def delete_campaign(
            self,
            db: Session,
            *,
            campaign_id: UUID4
    ):
        return db.query(models.postman.Campaign)\
            .filter(models.postman.Campaign.id == campaign_id).delete()

    def set_group_name(self, db: Session, *, campaign_id: UUID4, group_name: str) -> None:
        db_obj = db.query(self.model).filter(id == campaign_id).first()
        db_obj.group_name = group_name
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return


campaign = CampaignServices(models.postman.Campaign)
