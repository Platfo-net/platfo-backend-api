from sqlalchemy.orm import Session
import json

from datetime import timedelta
from app import services
from redis.client import Redis
from app.core.extra_classes import UserData


def get_data_from_cache(client: Redis, key: str = None) -> str:
    val = client.get(key)
    return val


def set_data_to_cache(
    client: Redis,
    key: str = None,
    value: str = None,
    expire: int = 3600
) -> bool:
    state = client.setex(key, timedelta(seconds=3600),
                         value=value)  # todo time
    client.expire(key, expire)
    return state


def get_user_data(
    client: Redis,
    db: Session,
    *,
    instagram_page_id: str = None
) -> UserData:
    data = get_data_from_cache(client, key=instagram_page_id)

    if data is None:
        instagram_page = services.instagram_page.get_page_by_instagram_page_id(
            db, instagram_page_id=instagram_page_id)

        data = dict(
            user_id=str(instagram_page.facebook_account.user_id),
            facebook_account_id=str(instagram_page.facebook_account_id),
            facebook_page_token=instagram_page.facebook_page_token,
            facebook_page_id=instagram_page.facebook_page_id,
            account_id=str(instagram_page.id)
        )
        data = json.dumps(data)
        state = set_data_to_cache(client, key=instagram_page_id, value=data)
        if state is True:
            data = get_data_from_cache(client, key=instagram_page_id)

    data = json.loads(data)

    return UserData(
        user_id=data["user_id"],
        facebook_account_id=data["facebook_account_id"],
        facebook_page_token=data["facebook_page_token"],
        facebook_page_id=data["facebook_page_id"],
        account_id=data["account_id"],
    )


def get_password_data(client: Redis, *, code: str = None):

    data = get_data_from_cache(client, key='code')

    if data is None:
        state = set_data_to_cache(client, key='code', value=code)
        if state is True:
            data = get_data_from_cache(client, key='code')
    return data
