

class InstagramData:
    def __init__(self,
                 id_sender: str = None,
                 id_recipient: str = None,
                 message_detail: str = None,
                 mid: str = None,
                 postback: dict = {},
                 payload: dict = {}):

        self.id_sender = id_sender
        self.id_recipient = id_recipient
        self.message_detail = message_detail
        self.mid = mid
        self.postback = postback
        self.payload = payload
        self.is_echo = False
        self.is_deleted = False
        self.mid = None
        self.attachment = None
        self.attachment_type = None
        self.story_url = None

    def parse(self, body):
        for element in body:
            messaging_list = element['messaging']
            for item in messaging_list:
                self.id_sender = item['sender']['id']
                self.id_recipient = item['recipient']['id']
                try:
                    try:
                        self.mid = item['message']['mid']
                    except Exception:
                        pass
                    
                    try:
                        self.mid = item["postback"]["mid"]
                    except Exception:
                        pass
                    try:
                        self.is_deleted = item['message']['is_deleted']
                    except Exception:
                        pass
                    try:
                        self.message_detail = item['message']['text']
                    except Exception:
                        pass
                    try:
                        self.is_echo = item["message"]["is_echo"]
                    except Exception:
                        pass
                    try:
                        self.attachment = item["message"]["attachments"][0]["payload"]["url"]
                    except Exception:
                        pass
                    try:
                        self.attachment_type = item["message"]["attachments"][0]["type"]
                    except Exception:
                        pass
                    try:
                        self.message_detail = item['postback']["title"]
                    except Exception:
                        pass
                    try:
                        self.payload = item['postback']['payload']
                    except Exception:
                        pass
                    try:
                        self.story_url = item["message"]["reply_to"]["story"]["url"]
                    except Exception:
                        pass
                except Exception:
                    pass

    def to_dict(self):
        return dict(
            id_sender=self.id_sender,
            id_recipient=self.id_recipient,
            message_detail=self.message_detail,
            mid=self.mid,
            postback=self.postback,
            payload=self.payload,
            is_echo=self.is_echo,
            story_url=self.story_url,
            attachment=self.attachment ,
            is_deleted=self.is_deleted,
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
