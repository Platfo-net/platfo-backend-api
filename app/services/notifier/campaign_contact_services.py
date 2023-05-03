import math
from typing import List
from app import models, schemas
from sqlalchemy.orm import Session

ModelType = models.notifier.CampaignContact
CreateSchemaType = schemas.notifier.CampaignContactCreate
UpdateSchemaType = schemas.notifier.CampaignContactUpdate


class CampaignContactServices:
    def __init__(self, model):
        self.model = model

    def get_campain_contacts(self, db: Session, *, campaign_id: int, page: int, page_size: int):
        contacts = db.query(self.model).filter(
            self.model.campaign_id == campaign_id
        ).join(self.model.contact).offset(page_size * (page - 1)).limit(page_size).all()

        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count,
        )

        return contacts, pagination

    def create_bulk(
            self, db: Session, *, contacts: List[CreateSchemaType], campaign_id: int
    ) -> List[ModelType]:

        db_obj = [
            self.model(
                contact_id=c.contact_id,
                campaign_id=campaign_id,
                contact_igs_id=c.contact_igs_id,
            )
            for c in contacts
        ]
        db.add_all(db_obj)
        db.commit()

        return db_obj

    def get_campaign_unsend_contacts(
            self, db: Session, *, campaign_id: int, count: int
    ):

        return db.query(self.model).filter(
            self.model.is_sent == False,  # noqa
            self.model.campaign_id == campaign_id,
        ).join(self.model.contact).limit(count).all()

    def get_campaign_unsend_contacts_count(self, db: Session, *, campaign_id: int):
        return (
            db.query(models.notifier.CampaignContact)
            .filter(
                models.notifier.CampaignContact.is_sent == False,  # noqa
                models.notifier.CampaignContact.campaign_id == campaign_id,
            )
            .count()
        )

    def get_all_contacts_count(self, db: Session, campaign_id: int):
        return (
            db.query(self.model)
            .filter(self.model.campaign_id == campaign_id)
            .count()
        )

    def get_all_sent_count(self, db: Session, campaign_id: int):
        return (
            db.query(self.model)
            .filter(
                self.model.campaign_id == campaign_id,
                self.model.is_sent == True,  # noqa
            )
            .count()
        )

    def get_all_seen_count(self, db: Session, campaign_id: int):
        return (
            db.query(models.notifier.CampaignContact)
            .filter(
                self.model.campaign_id == campaign_id,
                self.model.is_seen == True  # noqa
            )
            .count()
        )

    def delete_campaign_contact(self, db: Session, *, campaign_contact_id: int):
        return (
            db.query(self.model)
            .filter(self.model.CampaignContact.id == campaign_contact_id)
            .delete()
        )

    def change_send_status_bulk(
            self, db: Session, *, campaign_contacts_in: list[ModelType], is_sent: bool
    ):

        db_objs = []
        for campaign_contact in campaign_contacts_in:
            campaign_contact.is_sent = is_sent
            db_objs.append(campaign_contact)

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


campaign_contact = CampaignContactServices(models.notifier.CampaignContact)
