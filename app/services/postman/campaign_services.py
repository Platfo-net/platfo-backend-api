from typing import List, Optional
from pydantic import UUID4
from app import models, schemas
from sqlalchemy.orm import Session
from app.constants.campaign_status import CampaignStatus

ModelType = models.postman.Campaign


class CampaignServices:
    def __init__(self, model):
        self.model = model

    def get_active_campaigns(self, db: Session)-> List[ModelType]:
        return db.query(self.model).filter(
            self.model.is_draft == False,
            self.model.status == CampaignStatus.PENDING,
            self.model.is_active == False
        ).all()


campaign = CampaignServices(models.postman.Campaign)
