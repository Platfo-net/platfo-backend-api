import redis
import sys
import json

from datetime import timedelta
from fastapi.encoders import jsonable_encoder
from app import services
from app.core.config import settings
from app.db.session import SessionLocal


db = SessionLocal()


def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=1,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)


def get_data_from_cache(key: str) -> str:
    client = redis_connect()
    val = client.get(key)
    return val


def set_data_to_cache(key: str, value: str) -> bool:
    client = redis_connect()
    state = client.setex(key, timedelta(seconds=3600), value=value)
    return state


def commence_redis(id_recipient,
                   ):
    data = get_data_from_cache(key=id_recipient)
    if data is not None:
        data = json.loads(data)
        data["cache"] = True
        print('cacheeeeeeeeeeee shodeeeeeee', data)
        return data
    else:
        obj_from_db = services.instagram_page.get_page_by_ig_id(
            db, ig_id=id_recipient)
        facebook_data_from_db = jsonable_encoder(obj_from_db.facebook_account)
        instagram_data_from_db = jsonable_encoder(obj_from_db)
        data = dict(
            user_id=facebook_data_from_db['user_id'],
            facebook_account_id=instagram_data_from_db['facebook_account_id'],
            facebook_page_token=instagram_data_from_db['facebook_page_token'],
            facebook_page_id=instagram_data_from_db['facebook_page_id'],
            account_id=instagram_data_from_db['id']
            )
        if data:
            print('taze cache mikoneeeeeeeeee')
            data["cache"] = False
            data = json.dumps(data)
            state = set_data_to_cache(key=id_recipient, value=data)
            if state is True:
                return json.loads(data)
            return data  # noqa
        else:
            return Exception("No Redis Connection!") # noqa
