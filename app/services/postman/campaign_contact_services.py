from typing import List, Optional
from pydantic import UUID4
from app import models, schemas, services
from sqlalchemy.orm import Session

ModelType = models.postman.CampaignContact
CreateSchemaType = schemas.postman.CampaignContactCreate
UpdateSchemaType = schemas.postman.CampaignContactUpdate


class CampaignContactServices:
    def __init__(self, model):
        self.model = model

    def create_bulk(
            self,
            db: Session,
            *,
            contacts: List[CreateSchemaType],
            campaign_id: UUID4
    ) -> List[ModelType]:

        db_obj = [self.model(contact_id=c.contact_id,
                             campaign_id=campaign_id,
                             contact_igs_id=c.contact_igs_id) for c in contacts]
        db.add_all(db_obj)
        db.commit()

        return db_obj


campaign_contact = CampaignContactServices(models.postman.CampaignContact)
