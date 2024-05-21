import json
from datetime import timedelta

from redis.client import Redis


def get_data_from_cache(client: Redis, key: str = None) -> str:
    val = client.get(key)
    return val


def set_data_to_cache(
    client: Redis, key: str = None, value: str = None, expire: int = 3600
) -> bool:
    state = client.setex(key, timedelta(seconds=3600), value=value)  # todo time
    client.expire(key, expire)
    return state


def remove_data_from_cache(client: Redis, key: str = None):
    client.delete(key)
    return None


def get_password_data(client: Redis, *, code: str = None):
    data = get_data_from_cache(client, key='code')

    if data is None:
        state = set_data_to_cache(client, key='code', value=code)
        if state is True:
            data = get_data_from_cache(client, key='code')
    return data


def get_user_registeration_activation_code(
    client: Redis, phone_number: str, phone_country_code: str
):
    data = get_data_from_cache(client, f'{phone_country_code}{phone_number}')
    if data is None:
        return None

    data = json.loads(data)
    return data


def set_user_registeration_activation_code(
    client: Redis, phone_number: str, phone_country_code: str, code: int, token: str
):
    data = dict(code=code, token=token)
    key = f'{phone_country_code}{phone_number}'
    data = json.dumps(data)
    result = set_data_to_cache(client, key, data, expire=120)
    return result


def get_user_reset_password_code(client: Redis, phone_number, phone_country_code):

    data = get_data_from_cache(client, f'{phone_country_code}{phone_number}')
    if data is None:
        return None

    data = json.loads(data)
    return data


def set_user_reset_password_code(
        client: Redis,
        phone_number: str,
        phone_country_code: str,
        code,
        token
):
    data = dict(code=code, token=token)
    data = json.dumps(data)
    key = f'{phone_country_code}{phone_number}'
    result = set_data_to_cache(client, key, data, expire=120)
    return result


def get_user_registeration_activation_code_by_email(
    client: Redis,
    email: str,
):
    data = get_data_from_cache(client, email)
    if data is None:
        return None

    data = json.loads(data)
    return data


def set_user_registeration_activation_code_by_email(
    client: Redis, email: str, code: int, token: str
):
    data = dict(code=code, token=token)
    data = json.dumps(data)
    result = set_data_to_cache(client, email, data, expire=120)
    return result
