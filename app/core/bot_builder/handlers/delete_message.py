from app import services
from app.core.bot_builder.handlers.base import BaseHandler


class DeleteMessageHandler(BaseHandler):
    def __call__(self):
        services.live_chat.message.remove_message_by_mid(self.db, mid=self.instagram_data.mid)
