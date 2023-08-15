from datetime import datetime

from app import services
from app.core.instagram.handlers.base import BaseHandler


class DeleteMessageHandler(BaseHandler):
    def __call__(self):
        services.live_chat.message.remove_message_by_mid(self.db, mid=self.instagram_data.mid)

    def update_databoard(self):
        now = datetime.now()
        databoard = services.databoard.lead_message_stat.get(
            self.db,
            facebook_page_id=self.user_page_data.facebook_page_id,
            now=now
        )

        if databoard:
            services.databoard.lead_message_stat.update_count(
                self.db,
                db_obj=databoard,
                added_count=-1
            )

        return databoard
