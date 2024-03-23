

from datetime import datetime, timedelta

import pytz
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.constants.currency import Currency
from app.core.celery import celery
from app.core.telegram.tasks import send_shop_order_report_task
from app.db.session import SessionLocal


@celery.task
def calculate_shops_daily_report_task(from_datetime: datetime = None):
    db = SessionLocal()
    if from_datetime:
        from_datetime = from_datetime.astimezone(pytz.timezone("Asia/Tehran")).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        from_datetime = datetime.now().astimezone(pytz.timezone("Asia/Tehran")).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    to_datetime = from_datetime + timedelta(days=1)
    analytics = calculate_shop_daily_report(db, from_datetime, to_datetime)
    objs = []
    for analytic in analytics:
        obj = models.shop.ShopDailyReport(
            order_count=analytic[2],
            order_amount=analytic[1] if analytic[1] else 0,
            date=from_datetime.date(),
            shop_id=analytic[0],
            currency=Currency.IRT["value"],
        )
        objs.append(obj)
        send_shop_order_report_task.delay(
            "fa", obj.shop_id, obj.order_amount, obj.currency, obj.order_count, obj.date)
    db.add_all(objs)
    db.commit()

    return len(objs)


def calculate_shop_daily_report(db: Session, from_datetime, to_datetime):
    return db.query(
        models.shop.ShopOrder.shop_id,
        func.sum(models.shop.ShopOrder.total_amount),
        func.count(models.shop.ShopOrder.id),
    ).filter(
        models.shop.ShopOrder.created_at >= from_datetime,
        models.shop.ShopOrder.created_at < to_datetime,
    ).group_by(models.shop.ShopOrder.shop_id).all()
