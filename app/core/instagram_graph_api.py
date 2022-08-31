from typing import Dict, List, Union
from app.core.config import settings

import requests


class InstagramGraphApi:

    def send_text_message(
        self,
        text: str,
        quick_replies: List[dict],
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
                "text": text,
                "quick_replies":
                [
                    {
                        "content_type": "text",
                        "title": quick_reply["text"],
                        "payload": quick_reply["id"]
                    }
                    for quick_reply in quick_replies
                ] if len(quick_replies) else None
            }
        }

        params = {
            "access_token": page_access_token
        }

        res = requests.post(url, params=params, json=payload)
        print(res)
        print('javab isssssssssssss', res.json())

        return res.json()

    def send_menu(
            self,
            data,
            quick_replies,
            from_id: str,
            to_id: str,
            page_access_token: str):
        print(quick_replies)
        body = {
            "template_type": "generic",
            "elements": [
                {
                    "title": data["title"],
                    "buttons": [
                        {
                            "type": "postback",
                            "title": choice["text"],
                            "payload": choice["id"]
                        } for choice in data["choices"]
                    ],

                }
            ]
        }

        quick_replies = [
            {
                "content_type": "text",
                "title": quick_reply["text"],
                "payload": quick_reply["id"]
            } for quick_reply in quick_replies
        ] if len(quick_replies) else None
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
                "quick_replies": quick_replies,
                "attachment": {
                    "type": "template",
                    "payload": body
                }
            }
        }

        res = requests.post(url=url, params=params, json=payload)
        print('javabe 2 v0mi isssssssss', res.json())
        return res.status_code

    def get_contact_information_from_facebook(
        self,
        contact_igs_id: str = None,
        page_access_token: str = None
    ) -> Union[dict, None]:
        url = "{}/{}/{}".format(
            settings.FACEBOOK_GRAPH_BASE_URL,
            settings.FACEBOOK_GRAPH_VERSION,
            contact_igs_id
        )
        params = dict(
            fields="name,username,profile_pic,follower_count,"
            "is_user_follow_business,is_business_follow_user",
            access_token=page_access_token
        )
        res = requests.get(url=url, params=params)
        if res.status_code == 200:
            username = res.json()['username']
            profile_image = res.json()['profile_pic']
            return dict(username=username, profile_image=profile_image)

        return None


graph_api = InstagramGraphApi()
