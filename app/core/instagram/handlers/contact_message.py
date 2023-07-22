

from datetime import datetime
from uuid import uuid4

from app import services
from app.constants.message_direction import MessageDirection
from app.constants.widget_type import WidgetType
from app.core.instagram.instagram import SavedMessage
from app.core.instagram.handlers import BaseHandler
from app.core.instagram.handlers.base import BotBaseHandler


class ContactMessageHandler(BaseHandler):
    def __call__(self):
        saved_message = self.pack()
        _, self.is_new = self.save_message(saved_message)

        if saved_message.direction == MessageDirection.IN:
            self.update_databoard()

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
            timestamp=self.instagram_data.timestamp,
        )
        return saved_message

    def update_databoard(self):
        now = datetime.now()
        databoard = services.databoard.contact_message_stat.get(
            self.db,
            facebook_page_id=self.user_page_data.facebook_page_id,
            now=now
        )
        if not databoard:
            services.databoard.contact_message_stat.create(
                self.db,
                facebook_page_id=self.user_page_data.facebook_page_id,
                count=1,
                now=now
            )

        else:
            services.databoard.contact_message_stat.update_count(
                self.db,
                db_obj=databoard,
                added_count=1
            )

        if self.is_new:
            contact_databoard = services.databoard.contact_stat.get(
                self.db,
                facebook_page_id=self.user_page_data.facebook_page_id,
                now=now
            )
            if not contact_databoard:
                contact_databoard = services.databoard.contact_stat.create(
                    self.db,
                    facebook_page_id=self.user_page_data.facebook_page_id,
                    count=1,
                    now=now
                )
            else:
                services.databoard.contact_stat.update_count(
                    self.db,
                    db_obj=contact_databoard,
                    added_count=1,
                )

        return databoard


class ContactMessageBotHandler(BotBaseHandler):
    def run(self, trigger, application):
        if detail := self.check_connection_and_get_detail(trigger, application):
            chatflow_id = detail.get("chatflow_id")
            node = services.bot_builder.node.get_chatflow_head_node(
                self.db,
                chatflow_id=chatflow_id,
            )
            if not node:
                return

            self.send_widget(
                node.widget,
                chatflow_id,
                quick_replies=node.quick_replies,
                contact_igs_id=self.instagram_data.sender_id
            )
