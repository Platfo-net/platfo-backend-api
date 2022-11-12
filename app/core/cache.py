from sqlalchemy.orm import Session
import json

from datetime import timedelta
from app import services
from redis.client import Redis
from app.core.bot_builder.extra_classes import ConnectionData, UserData


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


def get_user_data(
    client: Redis, db: Session, *, instagram_page_id: str = None
) -> UserData:
    data = get_data_from_cache(client, key=instagram_page_id)

    if data is None:
        instagram_page = services.instagram_page.get_by_instagram_page_id(
            db, instagram_page_id=instagram_page_id
        )

        data = dict(
            user_id=str(instagram_page.user_id),
            facebook_page_token=instagram_page.facebook_page_token,
            facebook_page_id=instagram_page.facebook_page_id,
            account_id=str(instagram_page.id),
        )
        data = json.dumps(data)
        state = set_data_to_cache(client, key=instagram_page_id, value=data)
        if state is True:
            data = get_data_from_cache(client, key=instagram_page_id)

    data = json.loads(data)

    return UserData(
        user_id=data["user_id"],
        facebook_page_token=data["facebook_page_token"],
        facebook_page_id=data["facebook_page_id"],
        account_id=data["account_id"],
    )


def get_password_data(client: Redis, *, code: str = None):

    data = get_data_from_cache(client, key="code")

    if data is None:
        state = set_data_to_cache(client, key="code", value=code)
        if state is True:
            data = get_data_from_cache(client, key="code")
    return data


def get_connection_data(
    db: Session,
    client: Redis,
    *,
    application_name: str = None,
    account_id: str = None
):
    key = f"{application_name}+{str(account_id)}"
    data = get_data_from_cache(client, key)
    if data is None:
        connection = services.connection.get_by_application_name_and_account_id(
            db,
            account_id=account_id,
            application_name=application_name)

        if not connection:
            return None
        details = []
        for detail in connection.details:
            details.append(
                dict(chatflow_id=detail['chatflow_id'], trigger=detail['trigger']))

        data = dict(
            details=details,
        )
        data = json.dumps(data)
        state = set_data_to_cache(client, key=key, value=data, expire=3600)
        if state:
            data = get_data_from_cache(client, key=key)

    data = json.loads(data)

    return ConnectionData(
        account_id=account_id,
        application_name=application_name,
        details=data.get('details'),
    )


def get_node_chatflow_id(
    db: Session,
    client: Redis,
    *,
    widget_id: str = None
):
    data = get_data_from_cache(client, widget_id)
    data = str(data).strip("',/b")
    if data == 'None':
        try:
            node = services.bot_builder.node.get_next_node(
                db, from_id=widget_id)
        except Exception:
            return None

        state = set_data_to_cache(client, key=widget_id, value=str(node.chatflow_id))
        if not state:
            return None
        data = get_data_from_cache(client, key=widget_id)
        data = str(data).strip("',/b")

    return data
