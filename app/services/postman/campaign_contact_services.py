from typing import List
from pydantic import UUID4
from app import models, schemas
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
                             contact_igs_id=c.contact_igs_id)
                  for c in contacts]
        db.add_all(db_obj)
        db.commit()

        return db_obj

    def get_campaign_unsend_contacts(
            self,
            db: Session,
            *,
            campaign_id: UUID4,
            count: int
    ) -> List[ModelType]:

        return db.query(models.postman.CampaignContact)\
            .filter(
                models.postman.CampaignContact.is_sent == False,  # noqa
                models.postman.CampaignContact.campaign_id == campaign_id
        ).limit(count).all()

    def get_campaign_unsend_contacts_count(
            self,
            db: Session,
            *,
            campaign_id: UUID4
    ):
        return db.query(models.postman.CampaignContact) \
            .filter(
            models.postman.CampaignContact.is_sent == False,  # noqa
            models.postman.CampaignContact.campaign_id == campaign_id
        ).count()

    def get_all_contacts_count(
            self,
            db: Session,
            *,
            campaign_id: UUID4
    ):
        return db.query(models.postman.CampaignContact).\
            filter(models.postman.CampaignContact.campaign_id
                   == campaign_id).count()

    def get_all_sent_count(
            self,
            db: Session,
            *,
            campaign_id: UUID4
    ):
        return db.query(models.postman.CampaignContact).\
            filter(models.postman.CampaignContact.campaign_id == campaign_id,
                   models.postman.CampaignContact.is_sent is True).count()

    def get_all_seen_count(
            self,
            db: Session,
            *,
            campaign_id: UUID4
    ):
        return db.query(models.postman.CampaignContact).\
            filter(models.postman.CampaignContact.campaign_id == campaign_id,
                   models.postman.CampaignContact.is_seen is True).count()

    def delete_campaign_contact(
            self,
            db: Session,
            *,
            campaign_contact_id: UUID4
    ):
        return db.query(models.postman.CampaignContact)\
            .filter(models.postman.CampaignContact.id == campaign_contact_id)\
            .delete()

    def change_send_status_bulk(
        self,
        db: Session,
        *,
        campaign_contacts_in: list[ModelType],
        is_sent: bool
    ):

        db_objs = []
        for campaign_contact in campaign_contacts_in:
            campaign_contact.is_sent = is_sent
            db_objs.append(campaign_contact)

        db.add_all(db_objs)
        db.commit()
        return db_objs

    def seen_message(
        self,
        db: Session,
        *,
        mid: str
    ):
        db_obj = db.query(self.model).filter(self.model.mid == mid).first()
        if not db_obj:
            return
        db_obj.is_seen = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def remove_bulk(self, db: Session, *, campaign_id=UUID4):
        return db.query(self.model).filter(self.model.campaign_id == campaign_id).delete()


campaign_contact = CampaignContactServices(models.postman.CampaignContact)
