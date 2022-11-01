from datetime import datetime
import math
from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import and_

from app import models, schemas


class ContactServices:
    def __init__(self, model):
        self.model = model

    def create(
            self, db: Session, *, obj_in: schemas.live_chat.ContactCreate
    ) -> models.live_chat.Contact:
        obj_in = jsonable_encoder(obj_in)
        contact = self.model(**obj_in, information={}, last_message_at=datetime.now())
        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact

    def get(self, db: Session, *, id: UUID4):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_contact_by_igs_id(self, db: Session, *, contact_igs_id: str):
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
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )

        db_obj.information = information
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update_information(
            self,
            db: Session,
            *,
            contact_igs_id: str,
            data: dict,
    ):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.information.update(data)
        flag_modified(db_obj, "information")
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_pages_contacts(
            self, db: Session, *, page_id: str, skip: int = 0, limit: int = 100
    ):
        """Return an specific instagram page's contacts

        Args:
            page_id (str): Id of a instagram's facebook page
            skip (int, optional):
            limit (int, optional):

        Returns:
            List of contacts
        """
        return (
            db.query(self.model)
            .filter(self.model.user_page_id == page_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_last_message(
            self, db: Session, *, contact_igs_id: str, last_message: dict
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

    def update_last_comment_count(
            self, db: Session, *, contact_igs_id: str
    ):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.comment_count = db_obj.comment_count + 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def update_last_live_comment_count(
            self, db: Session, *, contact_igs_id: str
    ):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.live_comment_count = db_obj.live_comment_count + 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def update_last_message_count(
            self, db: Session, *, contact_igs_id: str
    ):
        db_obj = (
            db.query(self.model)
            .filter(self.model.contact_igs_id == contact_igs_id)
            .first()
        )
        db_obj.message_count = db_obj.message_count + 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    def remove_by_user_page_id(self, db: Session, *, user_page_id: str):
        contacts = (
            db.query(self.model).filter(self.model.user_page_id == user_page_id).all()
        )
        for contact in contacts:
            db.delete(contact)
        db.commit()
        return

    def get_bulk(
        self,
        db: Session,
        *,
        contacts_id: List[UUID4]
    ):
        contacts = []
        for contact_id in contacts_id:
            contacts.append(db.query(models.live_chat.Contact).
                            filter(models.live_chat.Contact.id == contact_id).first())
        return contacts

    def search(
            self,
            db: Session,
            *,
            obj_in: List[schemas.live_chat.SearchItem],
            page: int = 1,
            page_size: int = 20
    ):
        total_count = db.query(self.model).count()
        total_pages = math.ceil(total_count / page_size)
        pagination = schemas.Pagination(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count,
        )
        filters = []
        for obj in obj_in:
            print(obj)
            match obj.operator:
                case "eq":
                    filters.append(
                        getattr(models.live_chat.Contact, obj.field) == obj.value)
                case "ne":
                    filters.append(
                        getattr(models.live_chat.Contact, obj.field) != obj.value)
                case "gt":
                    filters.append(
                        getattr(models.live_chat.Contact, obj.field) > obj.value)

                case "lt":
                    filters.append(
                        getattr(models.live_chat.Contact, obj.field) < obj.value)

                case "gte":
                    filters.append(
                        getattr(models.live_chat.Contact, obj.field) >= obj.value)

                case "lte":
                    filters.append(
                        getattr(models.live_chat.Contact, obj.field) <= obj.value)

        return db.query(self.model).filter(and_(*filters)).all(), pagination


contact = ContactServices(models.live_chat.Contact)
