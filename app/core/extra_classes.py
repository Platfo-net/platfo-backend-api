

class InstagramData:
    def __init__(self,
                 id_sender: str = None,
                 id_recipient: str = None,
                 message_detail: str = None,
                 message_id: str = None,
                 postback: dict = {},
                 payload: dict = {}):

        self.id_sender = id_sender
        self.id_recipient = id_recipient
        self.message_detail = message_detail
        self.message_id = message_id
        self.postback = postback
        self.payload = payload

    def parse(self, body):
        for element in body:
            messaging_list = element['messaging']
            for item in messaging_list:
                self.id_sender = item['sender']['id']
                self.id_recipient = item['recipient']['id']
                try:
                    if item['message']:
                        self.message_id = item['message']['mid']
                        try:
                            self.message_detail = item['message']['text']
                        except Exception:
                            pass
                except Exception:
                    self.message_detail = item['postback']["title"]
                    # print(self.postback)
                    self.payload = item['postback']['payload']



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
