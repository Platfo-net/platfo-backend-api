from datetime import date

from sqlalchemy.orm import Session

from app import models


class DailyReportServices:
    def __init__(self, model):
        self.model: models.shop.ShopDailyReport = model

    def get_datetime_range_reports(
            self, db: Session, *, shop_id: int, from_date: date, to_date: date):
        return db.query(self.model).filter(
            self.model.shop_id == shop_id,
            self.model.date >= from_date,
            self.model.date < to_date,
        ).all()


daily_report = DailyReportServices(models.shop.ShopDailyReport)
