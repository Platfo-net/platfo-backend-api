

from datetime import datetime
from uuid import uuid4

from app import services
from app.constants.message_direction import MessageDirection
from app.constants.widget_type import WidgetType
from app.core.instagram.handlers import BaseHandler
from app.core.instagram.handlers.base import BotBaseHandler
from app.core.instagram.instagram import SavedMessage


class LeadMessageHandler(BaseHandler):
    def __call__(self):
        saved_message = self.pack()
        _, self.is_new = self.save_message(saved_message)

        if saved_message.direction == MessageDirection.IN:
            self.update_databoard()
        if self.is_new:
            services.instagram_page.update_leads_count(
                self.db,
                instagram_page_id=self.user_page_data.facebook_page_id
            )
        services.instagram_page.update_chats_count(
            self.db,
            instagram_page_id=self.user_page_data.facebook_page_id
        )

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
        databoard = services.databoard.lead_message_stat.get(
            self.db,
            facebook_page_id=self.user_page_data.facebook_page_id,
            now=now
        )
        if not databoard:
            services.databoard.lead_message_stat.create(
                self.db,
                facebook_page_id=self.user_page_data.facebook_page_id,
                count=1,
                now=now
            )

        else:
            services.databoard.lead_message_stat.update_count(
                self.db,
                db_obj=databoard,
                added_count=1
            )

        if self.is_new:
            lead_databoard = services.databoard.lead_stat.get(
                self.db,
                facebook_page_id=self.user_page_data.facebook_page_id,
                now=now
            )
            if not lead_databoard:
                lead_databoard = services.databoard.lead_stat.create(
                    self.db,
                    facebook_page_id=self.user_page_data.facebook_page_id,
                    count=1,
                    now=now
                )
            else:
                services.databoard.lead_stat.update_count(
                    self.db,
                    db_obj=lead_databoard,
                    added_count=1,
                )

        return databoard


class LeadMessageBotHandler(BotBaseHandler):
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
                widget=node.widget,
                chatflow_id=chatflow_id,
                quick_replies=node.quick_replies,
                lead_igs_id=self.instagram_data.sender_id
            )
