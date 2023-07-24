from app import services
from app.core.instagram.handlers.base import BotBaseHandler


class MessagePostbackBotHandler(BotBaseHandler):
    def run(self, application: str, postback_payload: str, chatflow_id: int):
        if services.connection.is_chatflow_connected_to_page(
                self.db,
                account_id=self.user_page_data.account_id,
                chatflow_id=chatflow_id,
                application_name=application,
        ):
            node = services.bot_builder.node.get_next_node(
                self.db,
                from_id=postback_payload,
                chatflow_id=chatflow_id,
            )
            if not node:
                return

            self.send_widget(
                widget=node.widget,
                quick_replies=node.quick_replies,
                chatflow_id=chatflow_id,
                contact_igs_id=self.instagram_data.sender_id,
            )
# chatflow_id = 1
# slides = {
#     "widget_type": "SLIDER",
#     "id": "37132f49-d49c-4e76-b1a4-e678494ba349",
#     "slides": [
#         {
#             "image":"",
#             "title" :"",
#             "subtitle" :"",
#             "choices" :[
#                 {"id": "d9344eff-b417-4721-8984-bb8fbffb21d0", "text": "My family"},
#                 {"id": "2e259e5b-2c3f-4da6-a7d6-fd95dec40ba5", "text": "My age"},
#                 {"id": "aa124532-2290-44c7-b0f5-3ec8cf8f4c86", "text": "My name"}
#             ]
#         },{
#             "image":"",
#             "title" :"",
#             "subtitle" :"",
#             "choices" :[
#                 {"id": "d9344eff-b417-4721-8984-bb8fbffb21d0", "text": "My family"},
#                 {"id": "2e259e5b-2c3f-4da6-a7d6-fd95dec40ba5", "text": "My age"},
#                 {"id": "aa124532-2290-44c7-b0f5-3ec8cf8f4c86", "text": "My name"}
#             ]
#         }
#     ]
# }
# from app.core import storage
# from app.core.config import settings
