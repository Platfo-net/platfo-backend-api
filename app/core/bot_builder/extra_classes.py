from dataclasses import dataclass

from app.constants.webhook_type import WebhookType


class InstagramData:
    def __init__(self, body):
        self.platform = None
        self.sender_id = None
        self.recipient_id = None
        self.text = None
        self.mid = None
        self.postback = None
        self.payload = None
        self.mid = None
        self.attachment = None
        self.attachment_type = None
        self.story_url = None
        self.url = None
        self.type = None
        self.timestamp = None
        self.is_deleted = False
        self.is_echo = False
        self.message_detail = None
        self.read = None
        self.field = None
        self.comment_detail = None
        self.media_id = None
        self.media_product_type = None
        self.username = None
        self.value_id = None
        self.parent_id = None
        self.entry_time = None
        self.parse(body)

    def parse(self, body):
        match body:
            case {
                'object': platform,
                'entry': [
                    {
                        'time': entry_time,
                        'id': entry_id,
                        'messaging': [
                            {
                                'sender': {'id': sender_id},
                                'recipient': {'id': recipient_id},
                                'timestamp': timestamp,
                                'postback': {
                                    'mid': mid,
                                    'title': title,
                                    'payload': payload,
                                },
                            }
                        ],
                    }
                ],
            }:
                self.platform = platform
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.title = title
                self.payload = payload
                self.type = WebhookType.MESSAGE_POSTBACK

            case {
                'object': platform,
                'entry': [
                    {
                        'id': recipient_id,
                        'time': entry_time,  # noqa
                        'changes': [
                            {
                                'field': field,
                                'value': {
                                    'from': {'id': sender_id, 'username': username},
                                    'media': {
                                        'id': media_id,
                                        'media_product_type': media_product_type,
                                    },
                                    'id': value_id,
                                    'parent_id': parent_id,
                                    'text': comment_detail,
                                },
                            }
                        ],
                    }
                ],
            }:
                self.recipient_id = recipient_id
                self.field = field
                self.sender_id = sender_id
                self.parent_id = parent_id
                self.platform = platform
                self.username = username
                self.media_id = media_id
                self.media_product_type = media_product_type
                self.comment_detail = comment_detail
                self.value_id = value_id
                self.type = WebhookType.COMMENT
                self.entry_time = entry_time

            case {
                'object': platform,
                'entry': [
                    {
                        'id': recipient_id,
                        'time': entry_time,  # noqa
                        'changes': [
                            {
                                'field': field,
                                'value': {
                                    'from': {'id': sender_id, 'username': username},
                                    'media': {
                                        'id': media_id,
                                        'media_product_type': media_product_type,
                                    },
                                    'id': value_id,
                                    'text': comment_detail,
                                },
                            }
                        ],
                    }
                ],
            }:
                self.recipient_id = recipient_id
                self.field = field
                self.sender_id = sender_id
                self.username = username
                self.media_id = media_id
                self.media_product_type = media_product_type
                self.comment_detail = comment_detail
                self.platform = platform
                self.value_id = value_id
                self.type = WebhookType.LIVE_COMMENT
                self.entry_time = entry_time

            case {
                'object': platform,
                'entry': [
                    {
                        'time': entry_time,  # noqa
                        'id': entry_id,  # noqa
                        'messaging': [
                            {
                                'sender': {'id': sender_id},
                                'recipient': {'id': recipient_id},
                                'timestamp': timestamp,
                                'read': {'mid': mid},
                            }
                        ],
                    }
                ],
            }:
                self.platform = platform
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.type = WebhookType.MESSAGE_SEEN

            case {
                'object': platform,
                'entry': [
                    {
                        'time': entry_time,
                        'id': entry_id,
                        'messaging': [
                            {
                                'sender': {'id': sender_id},
                                'recipient': {'id': recipient_id},
                                'timestamp': timestamp,
                                'message': {'mid': mid, 'text': text},
                            }
                        ],
                    }
                ],
            }:
                self.platform = platform
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.text = text
                self.type = WebhookType.CONTACT_MESSAGE

            case {
                'object': platform,
                'entry': [
                    {
                        'time': 1663574136816,
                        'id': '17841452052058552',
                        'messaging': [
                            {
                                'sender': {'id': sender_id},
                                'recipient': {'id': recipient_id},
                                'timestamp': timestamp,
                                'message': {
                                    'mid': mid,
                                    'text': text,
                                    'is_echo': is_echo,
                                },
                            }
                        ],
                    }
                ],
            }:
                self.platform = platform
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.text = text
                self.is_echo = is_echo
                self.type = WebhookType.CONTACT_MESSAGE_ECHO

            case {
                'object': platform,
                'entry': [
                    {
                        'time': entry_time,  # noqa
                        'id': entry_id,  # noqa
                        'messaging': [
                            {
                                'sender': {'id': sender_id},
                                'recipient': {'id': recipient_id},
                                'timestamp': timestamp,
                                'message': {'mid': mid, 'is_deleted': is_deleted},
                            }
                        ],
                    }
                ],
            }:
                self.platform = platform
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.is_deleted = is_deleted
                self.type = WebhookType.DELETE_MESSAGE

            case {
                'object': platform,
                'entry': [
                    {
                        'time': entry_time,  # noqa
                        'id': entry_id,  # noqa
                        'messaging': [
                            {
                                'sender': {'id': sender_id},
                                'recipient': {'id': recipient_id},
                                'timestamp': timestamp,
                                'message': {
                                    'mid': mid,
                                    'attachments': [
                                        {
                                            'type': 'story_mention',
                                            'payload': {'url': url},
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ],
            }:
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.url = url
                self.type = WebhookType.STORY_MENTION

            case _:
                pass

    def to_dict(self):
        return dict(
            platform=self.platform,
            sender_id=self.sender_id,
            recipient_id=self.recipient_id,
            text=self.text,
            postback=self.postback,
            payload=self.payload,
            mid=self.mid,
            attachment=self.attachment,
            story_url=self.story_url,
            url=self.url,
            type=self.type,
            timestamp=self.timestamp,
            is_deleted=self.is_deleted,
            is_echo=self.is_echo,
            read=self.read,
            field=self.field,
            comment_detail=self.comment_detail,
            media_id=self.media_id,
            media_product_type=self.media_product_type,
            username=self.username,
            value_id=self.value_id,
            parent_id=self.parent_id,
        )


class UserData:
    def __init__(self, user_id, facebook_page_token, facebook_page_id, account_id):
        self.user_id = user_id
        self.facebook_page_token = facebook_page_token
        self.facebook_page_id = facebook_page_id
        self.account_id = account_id

    def to_dict(self):
        return dict(
            user_id=self.user_id,
            facebook_page_token=self.facebook_page_token,
            facebook_page_id=self.facebook_page_id,
            account_id=self.account_id,
        )


class ConnectionData:
    def __init__(self, account_id, application_name, details):
        self.account_id = account_id
        self.application_name = application_name
        self.details = details

    def to_dict(self):
        return dict(
            account_id=self.account_id,
            application_name=self.application_name,
            details=self.details,
        )


@dataclass(init=True)
class SavedMessage:
    from_page_id: int = None
    to_page_id: int = None
    mid: str = None
    content: dict = None
    user_id: int = None
    direction: str = None
    instagram_page_id: int = None
    type: str = None
