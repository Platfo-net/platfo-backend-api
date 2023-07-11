from datetime import date, datetime

from sqlalchemy import func
from app import models
from app.services.databoard.databoard_base import DataboardBase
from sqlalchemy.orm import Session


class CommentStatServices(DataboardBase):
    def get_hourly_data(
            self,
            db: Session,
            *,
            from_date: date,
            to_date: date,
            facebook_page_id: int
    ):
        return db.query(self.model).filter(
            self.model.facebook_page_id == facebook_page_id,
            self.model.year >= from_date.year,
            self.model.year <= to_date.year,
            self.model.month >= to_date.month,
            self.model.month <= to_date.month,
            self.model.day >= to_date.day,
            self.model.day <= to_date.day,
        )

    def get_daily_data(
        self,
        db: Session,
        # *,
        from_date: date,
        to_date: date,
        facebook_page_id: int
    ):
        return db.query(
            self.model.year,
            self.model.month,
            self.model.day,
            func.sum(self.model.count),
        ).filter(
            self.model.facebook_page_id == facebook_page_id,
            self.model.from_datetime >= datetime.combine(from_date, datetime.min.time()),
            self.model.from_datetime <= datetime.combine(to_date, datetime.max.time()),
        ).order_by(
            self.model.year,
            self.model.month,
            self.model.day
        ).group_by(self.model.year, self.model.month, self.model.day).all()

    def get_monthly_data(
        self,
        db: Session,
        *,
        from_date: date,
        to_date: date,
        facebook_page_id: int
    ):
        return db.query(
            self.model.year,
            self.model.month,
            func.sum(self.model.count),
        ).filter(
            self.model.facebook_page_id == facebook_page_id,
            self.model.from_datetime >= datetime.combine(from_date, datetime.min.time()),
            self.model.from_datetime <= datetime.combine(to_date, datetime.max.time()),
        ).order_by(
            self.model.year,
            self.model.month,
        ).group_by(self.model.year, self.model.month).all()


comment_stat = CommentStatServices(models.databoard.CommentStat)
