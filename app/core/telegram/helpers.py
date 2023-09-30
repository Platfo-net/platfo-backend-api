from datetime import datetime
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
from app import services


def load_message(lang, template_name, **kwargs) -> str:
    file_path = f'app/templates/telegram/{lang}'
    file_loader = FileSystemLoader(file_path)
    env = Environment(loader=file_loader)
    template = env.get_template(f"{template_name}.txt")
    return template.render(**kwargs)


def has_credit_by_shop_id(db: Session, shop_id: int) -> bool:

    credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop_id)
    if not credit:
        return False
    return datetime.now() <= credit.expires_at


def has_credit_telegram_bot(db, shop_id):
    credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop_id)
    if not credit:
        return False
    return datetime.now() <= credit.expires_at
