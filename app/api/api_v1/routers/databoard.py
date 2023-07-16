from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.constants.timeframe import TimeFrame
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/databoard', tags=['Databoard'])


@router.get('/comments')
def get_comments_stats(
    *,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
    from_date: date,
    to_date: date,
    timeframe: str,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:

    page = services.instagram_page.get_by_facebook_page_id(db, facebook_page_id=facebook_page_id)

    if not page or page.user_id != current_user.id:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    if timeframe == TimeFrame.MONTHLY:
        report = services.databoard.comment_stat.get_monthly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.MonthlyStat(
                year=data[0],
                month=data[1],
                count=data[2],
            )
            for data in report
        ]

    if timeframe == TimeFrame.DAILY:
        report = services.databoard.comment_stat.get_daily_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.DailyStat(
                year=data[0],
                month=data[1],
                day=data[2],
                count=data[3],
            )
            for data in report
        ]

    if timeframe == TimeFrame.HOURLY:
        report = services.databoard.comment_stat.get_hourly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.HourlyStat(
                year=data.year,
                month=data.month,
                day=data.day,
                count=data.count,
            )
            for data in report
        ]

    raise_http_exception(Error.INVALID_TIMEFRAME)


@router.get('/contacts')
def get_contacts_stats(
    *,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
    from_date: date,
    to_date: date,
    timeframe: str,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:

    page = services.instagram_page.get_by_facebook_page_id(db, facebook_page_id=facebook_page_id)

    if not page or page.user_id != current_user.id:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    if timeframe == TimeFrame.MONTHLY:
        report = services.databoard.contact_stat.get_monthly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.MonthlyStat(
                year=data[0],
                month=data[1],
                count=data[2],
            )
            for data in report
        ]

    if timeframe == TimeFrame.DAILY:
        report = services.databoard.contact_stat.get_daily_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.DailyStat(
                year=data[0],
                month=data[1],
                day=data[2],
                count=data[3],
            )
            for data in report
        ]

    if timeframe == TimeFrame.HOURLY:
        report = services.databoard.contact_stat.get_hourly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.HourlyStat(
                year=data.year,
                month=data.month,
                day=data.day,
                count=data.count,
            )
            for data in report
        ]

    raise_http_exception(Error.INVALID_TIMEFRAME)


@router.get('/contact-messages')
def get_contact_messages_stats(
    *,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
    from_date: date,
    to_date: date,
    timeframe: str,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:

    page = services.instagram_page.get_by_facebook_page_id(db, facebook_page_id=facebook_page_id)

    if not page or page.user_id != current_user.id:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    if timeframe == TimeFrame.MONTHLY:
        report = services.databoard.contact_message_stat.get_monthly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.MonthlyStat(
                year=data[0],
                month=data[1],
                count=data[2],
            )
            for data in report
        ]

    if timeframe == TimeFrame.DAILY:
        report = services.databoard.contact_message_stat.get_daily_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.DailyStat(
                year=data[0],
                month=data[1],
                day=data[2],
                count=data[3],
            )
            for data in report
        ]

    if timeframe == TimeFrame.HOURLY:
        report = services.databoard.contact_message_stat.get_hourly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.HourlyStat(
                year=data.year,
                month=data.month,
                day=data.day,
                count=data.count,
            )
            for data in report
        ]

    raise_http_exception(Error.INVALID_TIMEFRAME)


@router.get('/live-comments')
def get_live_comments_stats(
    *,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
    from_date: date,
    to_date: date,
    timeframe: str,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:

    page = services.instagram_page.get_by_facebook_page_id(db, facebook_page_id=facebook_page_id)

    if not page or page.user_id != current_user.id:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    if timeframe == TimeFrame.MONTHLY:
        report = services.databoard.live_comment_stat.get_monthly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.MonthlyStat(
                year=data[0],
                month=data[1],
                count=data[2],
            )
            for data in report
        ]

    if timeframe == TimeFrame.DAILY:
        report = services.databoard.live_comment_stat.get_daily_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.DailyStat(
                year=data[0],
                month=data[1],
                day=data[2],
                count=data[3],
            )
            for data in report
        ]

    if timeframe == TimeFrame.HOURLY:
        report = services.databoard.live_comment_stat.get_hourly_data(
            db,
            from_date=from_date,
            to_date=to_date,
            facebook_page_id=facebook_page_id,
        )
        return [
            schemas.databoard.HourlyStat(
                year=data.year,
                month=data.month,
                day=data.day,
                count=data.count,
            )
            for data in report
        ]

    raise_http_exception(Error.INVALID_TIMEFRAME)
