import math
from typing import List, Optional
from pydantic import UUID4
from app import models, schemas, services
from sqlalchemy.orm import Session
from app.constants.campaign_status import CampaignStatus


class GroupContactServices:
    def __init__(self, model):
        self.model = model

    def create_bulk(self, db: Session, *, objs_in: List[schemas.postman.GroupContact], campaign_id: UUID4):
        db_objs = []
        for obj_in in objs_in:
            db_objs.append(
                self.model(
                    contact_igs_id=obj_in.contact_igs_id,
                    contact_id=obj_in.contact_id,
                    campaign_id=campaign_id
                )
            )

        db.add_all(db_objs)
        db.commit()
        db.refresh(db_objs)

    def remove_bulk(self, db: Session, *, campaign_id=UUID4):
        db.query(self.model).filter(self.model.campaign_id == campaign_id).delete()
        return


group_contact = GroupContactServices(models.postman.GroupContact)
