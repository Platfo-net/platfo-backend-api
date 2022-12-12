import logging
import random
import string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_string() -> str:
    return "".join(random.choices(string.ascii_letters, k=32))


def random_email() -> str:
    return f"{random_string()}@{random_string()}.com"


def random_widget_type() -> str:
    list_widget_type = [
        "MENU",
        "TEXT",
        "MEDIA",
    ]
    return random.choice(list_widget_type)
