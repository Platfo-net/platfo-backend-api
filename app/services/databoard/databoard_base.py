from datetime import datetime

from sqlalchemy.orm import Session


class DataboardBase:
    def __init__(self, model) -> None:
        self.model = model

    def create(self, db: Session, *, facebook_page_id: int, count: int = 1, now: datetime):
        db_obj = self.model(
            facebook_page_id=facebook_page_id,
            count=count,
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            from_datetime=now,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, facebook_page_id: int, now: datetime):
        return db.query(self.model).filter(
            self.model.facebook_page_id == facebook_page_id,
            self.model.year == now.year,
            self.model.month == now.month,
            self.model.day == now.day,
            self.model.hour == now.hour,
        ).first()

    def update_count(
        self,
        db: Session,
        *,
        db_obj,
        added_count: int,
    ):

        db_obj.count += added_count
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
