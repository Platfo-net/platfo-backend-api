from typing import Union
from app.core.config import settings

import requests

from app.core import storage


class InstagramGraphApi:

    def send_quick_replies(
        self,
        quick_replies,
        from_id: str,
        to_id: str,
        page_access_token: str
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
                "text": "...",
                "quick_replies":
                [
                    {
                        "content_type": "text",
                        "title": quick_reply["text"],
                        "payload": quick_reply["id"]
                    }
                    for quick_reply in quick_replies
                ]
            }
        }
        params = {
            "access_token": page_access_token
        }
        res = requests.post(url, params=params, json=payload)
        print(res)
        print('javab quick issssssssssssssss', res.json())

        return res.json()

    def send_text_message(
        self,
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
                "text": text,
            }
        }

        params = {
            "access_token": page_access_token
        }

        res = requests.post(url, params=params, json=payload)
        return res.json()

    def send_menu(
            self,
            data,
            quick_replies,
            from_id: str,
            to_id: str,
            page_access_token: str):

        from app.core import storage
        image_url = storage.get_object_url(data["image"],
                                           settings.S3_CHATFLOW_MEDIA_BUCKET)

        body = {
            "template_type": "generic",
            "elements": [
                {
                    "title": data["title"],
                    "image_url": image_url,
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

        print(body)
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
        if quick_replies:
            self.send_quick_replies(
                quick_replies,
                from_id,
                to_id,
                page_access_token)

        return res.json()

    def send_media(
        self,
        title,
        image,
        from_id: str,
        to_id: str,
        page_access_token: str
    ):
        image_url = storage.get_object_url(
            image,
            settings.S3_CHATFLOW_MEDIA_BUCKET
        )
        body = {
            "template_type": "generic",
            "elements": [
                {
                    "title": title,
                    "image_url": image_url,
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

        return res.json()

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
            fields="name,username,profile_pic,follower_count,is_verified_user,"
                   "is_user_follow_business,is_business_follow_user",
            access_token=page_access_token
        )
        res = requests.get(url=url, params=params)
        if res.status_code == 200:
            username = res.json()['username']
            profile_image = res.json()['profile_pic']
            name = res.json()['name']
            follower_count = res.json()['follower_count']
            is_verified_user = res.json()['is_verified_user']
            is_user_follow_business = res.json()['is_user_follow_business']
            is_business_follow_user = res.json()['is_business_follow_user']
            return dict(username=username,
                        profile_image=profile_image,
                        name=name,
                        follower_count=follower_count,
                        is_verified_user=is_verified_user,
                        is_user_follow_business=is_user_follow_business,
                        is_business_follow_user=is_business_follow_user)

        return None


graph_api = InstagramGraphApi()
