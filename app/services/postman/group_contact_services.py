from typing import List
from pydantic import UUID4
from app import models, schemas
from sqlalchemy.orm import Session


class GroupContactServices:
    def __init__(self, model):
        self.model = model

    def create_bulk(
        self,
        db: Session,
        *,
        objs_in: List[schemas.postman.GroupContact],
        group_id: UUID4
    ):
        db_objs = []
        for obj_in in objs_in:
            db_objs.append(
                self.model(
                    contact_igs_id=obj_in.contact_igs_id,
                    contact_id=obj_in.contact_id,
                    group_id=group_id
                )
            )

        db.add_all(db_objs)
        db.commit()

    def remove_bulk(self, db: Session, *, group_id=UUID4):
        return db.query(self.model).filter(self.model.group_id == group_id).delete()


group_contact = GroupContactServices(models.postman.GroupContact)
