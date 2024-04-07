from datetime import date, datetime, timedelta
from typing import Union
from uuid import uuid4

import jdatetime
import pytz
import requests
import telegram
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app import services
from app.core import storage
from app.core.config import settings


def load_message(lang: str, template_name: str, **kwargs) -> str:
    file_path = f'app/templates/telegram/{lang}'
    file_loader = FileSystemLoader(file_path)
    env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(f"{template_name}.txt")
    return template.render(**kwargs)


def has_credit_by_shop_id(db: Session, shop_id: int) -> bool:

    credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop_id)
    if not credit:
        return False
    return datetime.now() <= credit.expires_at


def has_credit_telegram_bot(db, shop_id):
    if settings.ENVIRONMENT != "prod":
        return True
    credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop_id)
    if not credit:
        return False
    return datetime.now() <= credit.expires_at


def get_expires_close_shops(db) -> dict[int, dict[str, Union[str, datetime]]]:
    lower = datetime.now()
    upper = datetime.now() - timedelta(days=5)
    shops_credit = services.credit.shop_credit.get_expire_between(db, lower=lower, upper=upper)
    shop_ids = [shop.shop_id for shop in shops_credit]
    bots = services.shop.shop_telegram_bot.get_multi_by_shop_ids(db, shop_ids=shop_ids)
    shops = {}
    for bot in bots:
        for shop_credit in shops_credit:
            if bot.shop_id == shop_credit.shop_id:
                shops[bot.shop_id] = {
                    "chat_id": bot.support_account_chat_id,
                    "expires_at": shop_credit.expires_at,
                }

    return shops


def number_to_price(number):
    number = list(reversed(list(str(number))))
    i = 0
    new_number = []
    for char in number:
        i += 1
        new_number.append(char)
        if i % 3 == 0 and i != len(number):
            new_number.append(",")
    new_number = reversed(new_number)
    return "".join(new_number)


async def download_and_upload_telegram_image(bot, photo_unique_id, bucket):
    res: telegram.File = await bot.get_file(file_id=photo_unique_id)
    if not res.file_path:
        return None, None
    file_path = res.file_path
    res = requests.get(file_path)

    if not res.status_code == 200:
        return None, None

    image_format = file_path.split(".")[-1]

    file_name = f"{uuid4()}.{image_format}"
    with open(file_name, "wb") as f:
        f.write(res.content)

    storage.add_file_to_s3(
        file_name, file_name, bucket)
    url = storage.get_object_url(file_name, bucket)
    return url, file_name


def get_credit_str(expires_at):
    iran_tz = pytz.timezone("Asia/Tehran")
    expires_at_datetime = expires_at.astimezone(iran_tz)
    jalali_date = jdatetime.GregorianToJalali(
        expires_at_datetime.year, expires_at_datetime.month, expires_at_datetime.day)
    date_str = f"{jalali_date.jyear}/{jalali_date.jmonth}/{jalali_date.jday}"
    time_str = f"{expires_at_datetime.hour}:{expires_at_datetime.minute}"

    return date_str, time_str


def get_jalali_date_str(date: date):
    jalali_date = jdatetime.GregorianToJalali(
        date.year, date.month, date.day)
    return f"{jalali_date.jyear}/{jalali_date.jmonth}/{jalali_date.jday}"
