from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.constants.campaign_status import CampaignStatus
from app.core.utils import paginate

ModelType = models.notifier.Campaign
CreateSchemaType = schemas.notifier.CampaignCreate
UpdateSchemaType = schemas.notifier.CampaignUpdate


class CampaignServices:
    def __init__(self, model):
        self.model = model

    def get_multi(
        self,
        db: Session,
        *,
        facebook_page_id: int = None,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ):
        condition = [self.model.user_id == user_id]
        if facebook_page_id:
            condition.append(self.model.facebook_page_id == facebook_page_id)

        campaigns = (
            db.query(self.model)
            .filter(and_(*condition))
            .offset(page_size * (page - 1))
            .limit(page_size)
            .all()
        )

        total_count = db.query(self.model).filter(and_(*condition)).count()
        return campaigns, paginate(total_count, page, page_size)

    def create(
        self, db: Session, *, obj_in: CreateSchemaType, user_id: int
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db_obj.user_id = user_id
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
        db_obj.content = obj_in.content
        db_obj.is_draft = obj_in.is_draft
        db_obj.user_id = user_id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_active_campaigns(self, db: Session):
        return (
            db.query(self.model)
            .filter(
                self.model.is_draft == False,  # noqa
                self.model.status == CampaignStatus.PENDING,
                self.model.is_active == False,  # noqa
            )
            .all()
        )

    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_uuid(self, db: Session, uuid: UUID4):
        return db.query(self.model).filter(self.model.uuid == uuid).first()

    def change_status(
        self,
        db: Session,
        *,
        id: int,
        status: str = CampaignStatus.DONE,
    ) -> ModelType:
        campaign = services.notifier.campaign.get(db=db, campaign_id=id)
        campaign.status = status

        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def change_is_draft(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        is_draft: bool,
    ) -> ModelType:
        db_obj.is_draft = is_draft

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def change_activity(
        self,
        db: Session,
        *,
        campaign_id: UUID4,
        is_active: bool,
    ) -> ModelType:
        campaign = services.notifier.campaign.get(db=db, campaign_id=campaign_id)
        campaign.is_active = is_active

        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def delete_campaign(self, db: Session, *, campaign_id: UUID4):
        return db.query(self.model).filter(self.model.id == campaign_id).delete()


campaign = CampaignServices(models.notifier.Campaign)
