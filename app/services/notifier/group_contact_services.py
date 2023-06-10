from typing import List

from sqlalchemy.orm import Session

from app import models, schemas


class GroupContactServices:
    def __init__(self, model):
        self.model = model

    def create_bulk(
        self,
        db: Session,
        *,
        objs_in: List[schemas.notifier.GroupContactCreate],
        group_id: int
    ):
        db_objs = []
        for obj_in in objs_in:
            db_objs.append(
                self.model(
                    contact_igs_id=obj_in.contact_igs_id,
                    contact_id=obj_in.contact_id,
                    group_id=group_id,
                )
            )

        db.add_all(db_objs)

        return db_objs

    def remove_bulk(self, db: Session, *, group_id=int):
        return db.query(self.model).filter(self.model.group_id == group_id).delete()

    def get_by_group(self, db: Session, *, group_id: int):
        return db.query(self.model).filter(self.model.group_id == group_id).all()

    def get_by_group_and_count(self, db: Session, *, group_id: int, count: int = 4):
        return (
            db.query(self.model)
            .filter(self.model.group_id == group_id)
            .limit(count)
            .all()
        )


group_contact = GroupContactServices(models.notifier.GroupContact)