import time
import requests

from app.core.celery_config import celery_app
from app.core.config import settings


@celery_app.task()
def send_message_to_contact_management(from_page_id,
                                       to_page_id,
                                       content,
                                       user_id,
                                       direction):
    url = "{}/contact-services/api/v1/message/".format(
        settings.CONTACT_MANAGEMENT_BASE_URL
    )
    res = requests.post(url, json={
        "from_page_id": from_page_id,
        "to_page_id": to_page_id,
        "content": content,
        "user_id": user_id,
        "direction": direction
    })


@celery_app.task()
def send_text_message(
        text: str,
        from_id: str,
        to_id: str,
        page_access_token: str,
):
    url = "{}/{}/{}/messages".format(
        settings.FACEBOOK_GRAPH_BASE_URL,
        settings.FACEBOOK_GRAPH_VERSION,
        from_id)

    payload = {
        "recipient": {
            'id': to_id,
        },
        "message": {
            "text": text
        }
    }

    params = {
        "access_token": page_access_token
    }

    res = requests.post(url, params=params, json=payload)
    print(res)
    print('javab isssssssssssss', res.json())

    return res.json()


@celery_app.task()
def send_batch_text_message(messages):
    for message in messages:
        url = "{}/{}/{}/messages".format(
            settings.FACEBOOK_GRAPH_BASE_URL,
            settings.FACEBOOK_GRAPH_VERSION,
            message["from_id"])

        payload = {
            "recipient": {
                'id': message["to_id"],
            },
            "message": {
                "text": message["text"]
            }
        }

        params = {
            "access_token": message["page_access_token"]
        }

        res = requests.post(url, params=params, json=payload)
        print(res)

    return 1


@celery_app.task()
def send_menu(data, from_id: str, to_id: str, page_access_token: str):
    body = {
        "template_type": "generic",
        "elements": [
            {
                "title": data["title"],
                # "default_action": {
                #   "type": "web_url",
                #   "url": "https://www.chatbot.aimedic.co/"
                # },
                "buttons": [
                    {
                        "type": "postback",
                        "title": choice["text"],
                        "payload": choice["id"]
                    } for choice in data["choices"]
                ]
            }
        ]
    }

    url = "{}/{}/{}/messages".format(
        settings.FACEBOOK_GRAPH_BASE_URL,
        settings.FACEBOOK_GRAPH_VERSION,
        from_id)

    params = {
        "access_token": page_access_token,
    }

    payload = {
        "recipient": {
            'id': to_id,
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": body
            }
        }
    }

    res = requests.post(url=url, params=params, json=payload)
    # print(res)
    print('javabe 2 v0mi isssssssss', res.json())
    return res.status_code


@celery_app.task()
def send_widget(widget, id_sender, payload, user_page_data):
    # print(user)
    while widget["widget_type"] == "MESSAGE":
        send_text_message.delay(
            text=widget["message"],
            from_id=user_page_data["facebook_page_id"],
            to_id=id_sender,
            page_access_token=user_page_data["facebook_page_token"]
        )

        send_message_to_contact_management.delay(
            from_page_id=user_page_data["facebook_page_id"],
            to_page_id=id_sender,
            content=widget,
            user_id=user_page_data["user_id"],
            direction="OUT"
        )

        payload = widget["id"]
        url = "{}/chatflow-services/api/v1/node/{}/next".format(
            settings.CHATFLOW_MANAGEMENT_BASE_URL,
            payload
        )
        time.sleep(0.5)
        res = requests.get(url=url)
        if res.status_code != 200:
            break
        widget = res.json()

    if widget["widget_type"] == "MENU":
        send_menu.delay(widget,
                        from_id=user_page_data["facebook_page_id"],
                        to_id=id_sender,
                        page_access_token=user_page_data["facebook_page_token"]
                        )
        send_message_to_contact_management.delay(
            from_page_id=user_page_data["facebook_page_id"],
            to_page_id=id_sender,
            content=widget,
            user_id=user_page_data["user_id"],
            direction="OUT"
        )
