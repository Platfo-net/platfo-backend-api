

from uuid import uuid4

from app import services
from app.constants.message_direction import MessageDirection
from app.constants.widget_type import WidgetType
from app.core.bot_builder.extra_classes import SavedMessage
from app.core.bot_builder.handlers import BaseHandler


class ContactMessageHandler(BaseHandler):
    def __call__(self):
        saved_message = self.pack()
        self.save_message(saved_message)

    def pack(self):
        saved_data = {
            'message': self.instagram_data.text,
            'widget_type': WidgetType.TEXT,
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


class ContactMessageBotHandler(BaseHandler):
    def run(self, detail, trigger, application):
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
                contact_igs_id=self.instagram_data.sender_id
            )
