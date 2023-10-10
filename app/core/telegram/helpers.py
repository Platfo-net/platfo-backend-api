from datetime import datetime, timedelta
from typing import Union

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app import services
from app.core.config import settings


def load_message(lang, template_name, **kwargs) -> str:
    file_path = f'app/templates/telegram/{lang}'
    file_loader = FileSystemLoader(file_path)
    env = Environment(loader=file_loader)
    template = env.get_template(f"{template_name}.txt")
    return template.render(**kwargs)


def has_credit_by_shop_id(db: Session, shop_id: int) -> bool:
    if settings.ENVIRONMENT != "prod":
        return True

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
