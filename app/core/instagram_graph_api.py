import requests
from app.core.config import settings


def send_text_message(
        text: str,
        from_id: str,
        to_id: str,
        page_access_token: str):

    url = "{}/{}/{}/messages".format(
        settings.FACEBOOK_GRAPH_BASE_URL,
        settings.FACEBOOK_GRAPH_VERSION,
        from_id)

    payload = {
        "recepient": {
            id: to_id,
        },
        "message": {
            "text": text
        }
    }

    params = {
        "access_token": page_access_token
    }

    res = requests.post(url, params=params, json=payload)

    return res.json()


def send_persistent_menu(
    items,
    from_id: str,
    to_id: str,
    page_access_token: str
):
    url = "{}/{}/{}/messenger_profile".format(
        settings.FACEBOOK_GRAPH_BASE_URL,
        settings.FACEBOOK_GRAPH_VERSION,
        from_id)

    params = {
        "access_token": page_access_token,
        "platform": "instagram"
    }
    call_to_actions = []

    for item in items:
        call_to_actions.append({
            "type": "postback",
            "title": item.text,
            "payload": item.id
        })

    body = {
        "recipient": {
            "id": to_id
        },
        "persistent_menu": [
            {
                "locale": "default",
                "call_to_actions": call_to_actions
            }
        ]
    }

    res = requests.post(url, params=params, json=body)
    return res.status_code
