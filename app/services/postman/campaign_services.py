from typing import List, Optional
from pydantic import UUID4
from app import models, schemas, services
from sqlalchemy.orm import Session
from app.constants.campaign_status import CampaignStatus

ModelType = models.postman.Campaign
CreateSchemaType = schemas.postman.CampaignCreate
UpdateSchemaType = schemas.postman.CampaignUpdate


class CampaignServices:
    def __init__(self, model):
        self.model = model

    def create(
            self,
            db: Session,
            *,
            obj_in: CreateSchemaType,
            user_id: UUID4
    ) -> ModelType:
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
        return db.query(self.model).filter(
            self.model.is_draft == False,
            self.model.status == CampaignStatus.PENDING,
            self.model.is_active == False
        ).all()

    def get(
        self,
        db: Session,
        *,
        campaign_id: UUID4
    ) -> ModelType:

        return db.query(models.postman.Campaign)\
            .filter(models.postman.Campaign.id == campaign_id).first()

    def change_status(
          self,
          db: Session,
          *,
          campaign_id: UUID4,
          status: CampaignStatus.DONE,
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


campaign = CampaignServices(models.postman.Campaign)
