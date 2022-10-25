from typing import List, Optional
from pydantic import UUID4
from app import models, schemas
from sqlalchemy.orm import Session
from app.constants.campaign_status import CampaignStatus

ModelType = models.postman.Campaign
CreateSchemaType = schemas.postman.CampaignCreate


class CampaignServices:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, *, obj_in: CreateSchemaType, user_id: UUID4) -> ModelType:
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

    def get_active_campaigns(self, db: Session) -> List[ModelType]:
        return db.query(self.model).filter(
            self.model.is_draft == False,
            self.model.status == CampaignStatus.PENDING,
            self.model.is_active == False
        ).all()


campaign = CampaignServices(models.postman.Campaign)
