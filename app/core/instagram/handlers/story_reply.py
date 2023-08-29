

from uuid import uuid4

from app import services
from app.constants.message_direction import MessageDirection
from app.core.instagram.handlers import BaseHandler, BotBaseHandler
from app.core.instagram.instagram import SavedMessage


class StoryReplyHandler(BaseHandler):

    def __call__(self):
        saved_message = self.pack()
        self.save_message(saved_message)

    def pack(self):
        saved_data = {
            'url': self.instagram_data.story_url,
            'widget_type': 'STORY_REPLY',
            'message': self.instagram_data.message_detail,
            'id': str(uuid4()),
        }
        saved_message = SavedMessage(
            from_page_id=self.instagram_data.sender_id,
            to_page_id=self.user_page_data.facebook_page_id,
            mid=self.instagram_data.mid,
            content=saved_data,
            user_id=self.user_page_data.user_id,
            direction=MessageDirection.IN,
            instagram_page_id=self.instagram_data.recipient_id,
        )
        return saved_message


class StoryReplyBotHandler(BotBaseHandler):

    def run(self, trigger, application):
        if detail := self.check_connection_and_get_detail(trigger, application):

            node = services.bot_builder.node.get_chatflow_head_node(
                self.db,
                chatflow_id=detail.get("chatflow_id"),
            )
            if not node:
                return

            self.send_widget(
                node.widget,
                quick_replies=node.quick_replies,
                lead_igs_id=self.instagram_data.sender_id
            )
