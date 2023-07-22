from typing import Union

import requests

from app.constants.button_type import ButtonType
from app.core import storage
from app.core.config import settings


class InstagramGraphApi:
    def send_quick_replies(
        self, quick_replies, from_id: str, to_id: str, page_access_token: str
    ):
        url = '{}/{}/{}/messages'.format(
            settings.FACEBOOK_GRAPH_BASE_URL, settings.FACEBOOK_GRAPH_VERSION, from_id
        )

        payload = {
            'recipient': {
                'id': to_id,
            },
            'message': {
                'text': '...',
                'quick_replies': [
                    {
                        'content_type': 'text',
                        'title': quick_reply['text'],
                        'payload': quick_reply['id'],
                    }
                    for quick_reply in quick_replies
                ],
            },
        }
        params = {'access_token': page_access_token}
        res = requests.post(url, params=params, json=payload)

        return res.json()

    def send_text_message(
        self,
        text: str,
        from_id: int,
        to_id: int,
        page_access_token: str,
        quick_replies: list = [],
    ):
        url = '{}/{}/{}/messages'.format(
            settings.FACEBOOK_GRAPH_BASE_URL, settings.FACEBOOK_GRAPH_VERSION, from_id
        )

        payload = {
            'recipient': {
                'id': to_id,
            },
            'message': {'text': text},
        }
        if len(quick_replies):
            payload['message']['quick_replies'] = [
                {
                    'content_type': 'text',
                    'title': quick_reply['text'],
                    'payload': quick_reply['id'],
                }
                for quick_reply in quick_replies
            ]

        params = {'access_token': page_access_token}

        res = requests.post(url, params=params, json=payload)
        mid = None
        if res.status_code == 200:
            mid = res.json()['message_id']
        return mid

    def send_menu(
        self,
        data,
        from_id: str,
        to_id: str,
        chatflow_id: int,
        page_access_token: str,
        quick_replies: list = [],
    ):
        choices = data.get('choices', [])
        buttons = []
        for choice in choices:
            button_type = data.get('type', None)
            if button_type == ButtonType.WEB_URL['name']:
                buttons.append(
                    {
                        'type': ButtonType.WEB_URL['value'],
                        'title': choice['text'],
                        'url': choice['url'],
                    }
                )
            else:
                buttons.append(
                    {
                        'type': ButtonType.POSTBACK['value'],
                        'title': choice['text'],
                        'payload': f"{choice['id']},{chatflow_id}",
                    }
                )

        body = {
            'template_type': 'generic',
            'elements': [{'title': data.get('title'), 'buttons': buttons}],
        }
        if 'image' in data:
            image_url = storage.get_object_url(
                data['image'], settings.S3_CHATFLOW_MEDIA_BUCKET
            )

            body['elements'][0]['image_url'] = image_url

        url = '{}/{}/{}/messages'.format(
            settings.FACEBOOK_GRAPH_BASE_URL, settings.FACEBOOK_GRAPH_VERSION, from_id
        )

        params = {
            'access_token': page_access_token,
        }

        payload = {
            'recipient': {
                'id': to_id,
            },
            'message': {'attachment': {'type': 'template', 'payload': body}},
        }

        res = requests.post(url=url, params=params, json=payload)
        if quick_replies:
            self.send_quick_replies(quick_replies, from_id, to_id, page_access_token)

        mid = None
        if res.status_code == 200:
            mid = res.json()['message_id']

        return mid

    def send_media(
        self, text, image_url, from_id: str, to_id: str, page_access_token: str
    ):
        body = {
            'template_type': 'generic',
            'elements': [
                {
                    'title': text,
                    'image_url': image_url,
                }
            ],
        }

        url = '{}/{}/{}/messages'.format(
            settings.FACEBOOK_GRAPH_BASE_URL, settings.FACEBOOK_GRAPH_VERSION, from_id
        )

        params = {
            'access_token': page_access_token,
        }

        payload = {
            'recipient': {
                'id': to_id,
            },
            'message': {'attachment': {'type': 'template', 'payload': body}},
        }

        res = requests.post(url=url, params=params, json=payload)
        mid = None
        if res.status_code == 200:
            mid = res.json().get('message_id', None)

        return mid

    def get_contact_information_from_facebook(
        self, contact_igs_id: str = None, page_access_token: str = None
    ) -> Union[dict, None]:
        url = '{}/{}/{}'.format(
            settings.FACEBOOK_GRAPH_BASE_URL,
            settings.FACEBOOK_GRAPH_VERSION,
            contact_igs_id,
        )
        params = dict(
            fields='name,username,profile_pic,follower_count,is_verified_user,'
            'is_user_follow_business,is_business_follow_user',
            access_token=page_access_token,
        )
        res = requests.get(url=url, params=params)
        if res.status_code == 200:
            data = res.json()
            return dict(
                username=data.get('username', None),
                profile_image=data.get('profile_pic', None),
                name=data.get('name', None),
                followers_count=data.get('follower_count', None),
                is_verified_user=data.get('is_verified_user', None),
                is_user_follow_business=data.get('is_user_follow_business', None),
                is_business_follow_user=data.get('is_business_follow_user', None),
            )
        return None


graph_api = InstagramGraphApi()
