from app.constants.webhook_type import WebhookType


class InstagramData:
    def __init__(self):
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

    def parse(self, body):
        match body:
            case {
                "object": platform,
                "entry": [
                    {
                        "time": 1660392271172,
                        "id": "17841449720273509",
                        "messaging": [
                            {
                    "sender": {
                        "id": sender_id
                    },
                    "recipient": {
                        "id": recipient_id
                    },
                    "timestamp": timestamp,
                    "postback": {
                        "mid": mid,
                        "title": title,
                        "payload": payload
                    }
                                }
                        ]
                    }
                ]
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
                "object": platform,
                "entry": [
                    {
                        "time": 1660389485931,
                        "id": "17841449720273509",
                        "messaging": [
                            {
                                "sender": {
                                    "id": sender_id
                                },
                                "recipient": {
                                    "id": recipient_id
                                },
                                "timestamp": timestamp,
                                "message": {
                                    "mid": mid,
                                    "text": text
                                }
                            }
                        ]
                    }
                ]
            }:
                self.platform = platform
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.text = text
                self.type = WebhookType.CONTACT_MESSAGE

            case {
                "object": platform,
                "entry": [
                    {
                        "time": 1663574136816,
                        "id": "17841452052058552",
                        "messaging": [
                            {
                    "sender": {
                        "id": sender_id
                    },
                    "recipient": {
                        "id": recipient_id
                    },
                    "timestamp": timestamp,
                    "message": {
                        "mid": mid,
                        "text": text,
                        "is_echo": is_echo
                    }
                                }
                        ]
                    }
                ]
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
                "object": platform,
                "entry": [
                    {
                        "time": 1663574281056,
                        "id": "17841452052058552",
                        "messaging": [
                            {
                    "sender": {
                        "id": sender_id
                    },
                    "recipient": {
                        "id": recipient_id
                    },
                    "timestamp": timestamp,
                    "message": {
                        "mid": mid,
                        "is_deleted": is_deleted
                    }
                                }
                        ]
                    }
                ]
            }:
                self.platform = platform
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.is_deleted = is_deleted
                self.type = WebhookType.DELETE_MESSAGE

            case {
                "object": platform,
                "entry": [
                    {
                        "time": 1663489987699,
                        "id": "17841452052058552",
                        "messaging": [
                            {
                    "sender": {
                        "id": sender_id
                    },
                    "recipient": {
                        "id": recipient_id
                    },
                    "timestamp": timestamp,
                    "message": {
                        "mid": mid,
                        "attachments": [
                            {
                                "type": "story_mention",
                                "payload": {
                                    "url": url
                                }
                            }
                        ]
                    }
                                }
                        ]
                    }
                ]
            }:
                self.sender_id = sender_id
                self.recipient_id = recipient_id
                self.timestamp = timestamp
                self.mid = mid
                self.url = url
                self.type = WebhookType.STORY_MENTION

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
        )


class UserData:
    def __init__(self, user_id,
                 facebook_account_id,
                 facebook_page_token,
                 facebook_page_id,
                 account_id):
        self.user_id = user_id
        self.facebook_account_id = facebook_account_id
        self.facebook_page_token = facebook_page_token
        self.facebook_page_id = facebook_page_id
        self.account_id = account_id

    def to_dict(self):
        return dict(
            user_id=self.user_id,
            facebook_account_id=self.facebook_account_id,
            facebook_page_token=self.facebook_page_token,
            facebook_page_id=self.facebook_page_id,
            account_id=self.account_id,
        )
