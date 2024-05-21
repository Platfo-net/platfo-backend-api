import math
import random
import re
import string
from datetime import datetime, timedelta
from typing import Tuple

import pytz

from app import schemas


def validate_password(password) -> bool:
    if len(password) < 8:
        return False
    elif re.search('[0-9]', password) is None:
        return False
    elif re.search('[A-Z]', password) is None:
        return False
    elif re.search('[a-z]', password) is None:
        return False
    return True


def generate_random_token(length: int) -> str:
    return ''.join(random.choice(f'{string.ascii_letters}0123456789') for _ in range(length))


def generate_random_code(length: int) -> int:
    return random.randint(10 ** length, (10 ** (length + 1)) - 1)


def paginate(total_count, page, page_size) -> schemas.Pagination:
    if page_size <= 0:
        page_size = 1
    return schemas.Pagination(
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total_count / page_size),
        total_count=total_count,
    )


def generate_random_support_token(length: int) -> str:
    token = ''.join(random.choice(string.digits) for _ in range(length))
    return "P" + token


def generate_random_short_url(length: int) -> str:
    token = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    return token


def get_today_datetime_range() -> Tuple[datetime, datetime]:
    from_datetime = datetime.now().astimezone(pytz.timezone("Asia/Tehran")).replace(
        hour=0, minute=0, second=0, microsecond=0)

    to_datetime = from_datetime + timedelta(days=1)
    return from_datetime, to_datetime


def decrease_cost_from_credit(credit_service, user_id, amount):
    credit = credit_service.get_or_create_by_user_id(user_id)
    credit_service.decrease_credit(credit, amount)
