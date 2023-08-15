from typing import List

from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import paginate

ModelType = models.notifier.CampaignLead
CreateSchemaType = schemas.notifier.CampaignLeadCreate
UpdateSchemaType = schemas.notifier.CampaignLeadUpdate


class CampaignLeadServices:
    def __init__(self, model):
        self.model = model

    def get_campaign_leads(
        self, db: Session, *, campaign_id: int, page: int, page_size: int
    ):
        leads = (
            db.query(self.model)
            .filter(self.model.campaign_id == campaign_id)
            .join(self.model.lead)
            .offset(page_size * (page - 1))
            .limit(page_size)
            .all()
        )
        total_count = db.query(self.model).filter(self.model.campaign_id == campaign_id).count()

        return leads, paginate(total_count, page, page_size)

    def create_bulk(
        self, db: Session, *, leads: List[CreateSchemaType], campaign_id: int
    ) -> List[ModelType]:
        db_obj = [
            self.model(
                lead_id=c.lead_id,
                campaign_id=campaign_id,
                lead_igs_id=c.lead_igs_id,
            )
            for c in leads
        ]
        db.add_all(db_obj)
        db.commit()

        return db_obj

    def get_campaign_unsend_leads(
        self, db: Session, *, campaign_id: int, count: int
    ):
        return (
            db.query(self.model)
            .filter(
                self.model.is_sent == False,  # noqa
                self.model.campaign_id == campaign_id,
            )
            .join(self.model.lead)
            .limit(count)
            .all()
        )

    def get_campaign_unsend_leads_count(self, db: Session, *, campaign_id: int) -> int:
        return (
            db.query(models.notifier.CampaignLead)
            .filter(
                models.notifier.CampaignLead.is_sent == False,  # noqa
                models.notifier.CampaignLead.campaign_id == campaign_id,
            )
            .count()
        )

    def get_all_leads_count(self, db: Session, campaign_id: int) -> int:
        return (
            db.query(self.model).filter(self.model.campaign_id == campaign_id).count()
        )

    def get_all_sent_count(self, db: Session, campaign_id: int) -> int:
        return (
            db.query(self.model)
            .filter(
                self.model.campaign_id == campaign_id,
                self.model.is_sent == True,  # noqa
            )
            .count()
        )

    def get_all_seen_count(self, db: Session, campaign_id: int) -> int:
        return (
            db.query(models.notifier.CampaignLead)
            .filter(
                self.model.campaign_id == campaign_id,
                self.model.is_seen == True,  # noqa
            )
            .count()
        )

    def delete_campaign_lead(self, db: Session, *, campaign_lead_id: int) -> int:
        return (
            db.query(self.model)
            .filter(self.model.CampaignLead.id == campaign_lead_id)
            .delete()
        )

    def change_send_status_bulk(
        self, db: Session, *, campaign_leads_in: list[ModelType], is_sent: bool
    ):
        db_objs = []
        for campaign_lead in campaign_leads_in:
            campaign_lead.is_sent = is_sent
            db_objs.append(campaign_lead)

        db.add_all(db_objs)
        db.commit()
        return db_objs

    def seen_message(self, db: Session, *, mid: str):
        db_obj = db.query(self.model).filter(self.model.mid == mid).first()
        if not db_obj:
            return
        db_obj.is_seen = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def remove_bulk(self, db: Session, *, campaign_id: int):
        return (
            db.query(self.model).filter(self.model.campaign_id == campaign_id).delete()
        )


campaign_lead = CampaignLeadServices(models.notifier.CampaignLead)
