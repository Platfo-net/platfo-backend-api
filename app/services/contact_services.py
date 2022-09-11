from pydantic import UUID4
from fastapi.encoders import jsonable_encoder
from app import models, schemas
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified


class ContactServices:
    def __init__(self, model):
        self.model = model

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.ContactCreate
    ) -> models.Contact:
        obj_in = jsonable_encoder(obj_in)
        contact = self.model(
            **obj_in,
            information={},
            last_message_at=datetime.now()
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact

    def get(self, db: Session, *, id: UUID4):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_contact_by_igs_id(self, db: Session, *, contact_igs_id: str):
        return db.query(self.model).filter(
            self.model.contact_igs_id == contact_igs_id
        ).first()

    def set_information(
        self,
        db: Session,
        *,
        contact_igs_id: str,
        information: dict,
    ):
        db_obj = db.query(self.model).filter(
            self.model.contact_igs_id == contact_igs_id).first()

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
        db_obj = db.query(self.model).filter(
            self.model.contact_igs_id == contact_igs_id).first()
        db_obj.information.update(data)
        flag_modified(db_obj, 'information')
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_pages_contacts(
        self,
        db: Session,
        *,
        page_id: str,
        skip: int = 0,
        limit: int = 100
    ):
        # -> List[schemas.Contact]:
        """Return an specific instagram page's contacts

        Args:
            page_id (str): Id of a instagram's facebook page
            skip (int, optional):
            limit (int, optional):

        Returns:
            List of contacts
        """
        return db.query(self.model).filter(
            self.model.user_page_id == page_id
        ).offset(skip).limit(limit).all()

    def update_last_message(
        self,
        db: Session,
        *,
        contact_igs_id: str,
        last_message: dict
    ):

        db_obj: models.Contact = db.query(self.model).filter(
            self.model.contact_igs_id == contact_igs_id
        ).first()

        db_obj.last_message = last_message
        db_obj.last_message_at = datetime.now()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    
    def remove_by_user_page_id(
        self,
        db: Session,
        *,
        user_page_id: str
    ):

        contacts =  db.query(self.model).filter(
            self.model.user_page_id == user_page_id
        ).all()
        for contact in contacts:
            db.delete(contact)
        db.commit()
        return



contact = ContactServices(models.Contact)
