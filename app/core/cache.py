import requests
import redis
import sys
import json
from datetime import timedelta
from app.core.config import settings


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


def commence_redis(id_recipient) -> dict:

    data = get_data_from_cache(key=id_recipient)
    if data is not None:
        data = json.loads(data)
        data["cache"] = True
        print('cacheeeeeeeeeeee   shodeeeeeee', data)
        return data
    else:
        url = "{}/user-services/api/v1/instagram/get/{}".format(
                    settings.USER_MANAGEMENT_BASE_URL,
                    id_recipient
                )
        user_service_response = requests.get(url=url)
        if user_service_response.status_code == 200:
            user_service_response = user_service_response.json()
            data = dict(user_id=user_service_response['facebook_account']
                        ["user_id"],
                        facebook_page_token=user_service_response
                        ['facebook_page_token'],
                        facebook_page_id=user_service_response
                        ['facebook_page_id'],
                        facebook_account_id=user_service_response
                        ['facebook_account_id'],
                        account_id=user_service_response['id'])
            print('taze cache mikiineeeeeeeeeeeeeee', data)
            data["cache"] = False
            data = json.dumps(data)
            state = set_data_to_cache(key=id_recipient, value=data)
            if state is True:
                return json.loads(data)
            return data  # noqa
        else:
            return Exception("No Redis Connection!") # noqa
