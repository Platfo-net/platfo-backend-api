import math
from datetime import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app import models, schemas


class ContactServices:
    def __init__(self, model):
        self.model = model

    def create(
        self, db: Session, *, obj_in: schemas.live_chat.ContactCreate
    ) -> models.live_chat.Contact:
        obj_in = jsonable_encoder(obj_in)
        contact = self.model(**obj_in, last_message_at=datetime.now())
        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact

    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_uuid(self, db: Session, uuid: UUID4):
        return db.query(self.model).filter(self.model.uuid == uuid).first()

    def get_contact_by_igs_id(self, db: Session, *, contact_igs_id: int):
        return (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )

    def set_information(
        self,
        db: Session,
        *,
        contact_igs_id: str,
        information: dict,
    ):
        db_obj: models.live_chat.Contact = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )

        db_obj.username = information.get("username")
        db_obj.name = information.get("name")
        db_obj.profile_image = information.get("profile_image")
        db_obj.followers_count = information.get("followers_count")
        db_obj.is_verified_user = information.get("is_verified_user")
        db_obj.is_user_follow_business = information.get("is_user_follow_business")
        db_obj.is_business_follow_user = information.get("is_business_follow_user")
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update_information(
        self,
        db: Session,
        *,
        contact_igs_id: int,
        data: dict,
    ):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.information.update(data)
        flag_modified(db_obj, 'information')
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_last_message(
        self, db: Session, *, contact_igs_id: int, last_message: str
    ):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )

        db_obj.last_message = last_message
        db_obj.last_message_at = datetime.now()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def update_last_comment_count(self, db: Session, *, contact_igs_id: int):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.comment_count = db_obj.comment_count + 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def update_last_live_comment_count(self, db: Session, *, contact_igs_id: int):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.live_comment_count = db_obj.live_comment_count + 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def update_last_message_count(self, db: Session, *, contact_igs_id: int):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.message_count = db_obj.message_count + 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def remove_by_user_page_id(self, db: Session, *, user_page_id: int):
        contacts = (
            db.query(self.model).filter(self.model.user_page_id == user_page_id).all()
        )
        for contact in contacts:
            db.delete(contact)
        db.commit()

        return

    def get_bulk(self, db: Session, *, contacts_id: List[int]):
        return (
            db.query(self.model)
            .filter(models.live_chat.Contact.id.in_(contacts_id))
            .all()
        )

    def get_bulk_by_uuid(self, db: Session, *, contacts_id: List[UUID4]):
        return (
            db.query(self.model)
            .filter(models.live_chat.Contact.uuid.in_(contacts_id))
            .all()
        )

    def get_multi(
        self,
        db: Session,
        *,
        facebook_page_id: int = None,
        obj_in: List[schemas.live_chat.SearchItem],
        page: int = 1,
        page_size: int = 20,
    ):
        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count,
        )
        filters = [models.live_chat.Contact.user_page_id == facebook_page_id]
        if len(obj_in):
            for obj in obj_in:
                match obj.operator:
                    case 'EQ':
                        filters.append(
                            getattr(models.live_chat.Contact, obj.field) == obj.value
                        )
                    case 'NE':
                        filters.append(
                            getattr(models.live_chat.Contact, obj.field) != obj.value
                        )
                    case 'GT':
                        filters.append(
                            getattr(models.live_chat.Contact, obj.field) > obj.value
                        )
                    case 'LT':
                        filters.append(
                            getattr(models.live_chat.Contact, obj.field) < obj.value
                        )

                    case 'GTE':
                        filters.append(
                            getattr(models.live_chat.Contact, obj.field) >= obj.value
                        )

                    case 'LTE':
                        filters.append(
                            getattr(models.live_chat.Contact, obj.field) <= obj.value
                        )

        return db.query(self.model).filter(and_(*filters)).all(), pagination


contact = ContactServices(models.live_chat.Contact)
