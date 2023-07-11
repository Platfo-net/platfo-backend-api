

from datetime import datetime

from app import services
from app.core.bot_builder.handlers.base import BaseHandler


class LiveCommentHandler(BaseHandler):
    def __call__(self):
        self.save_comment(
            db=self.db,
            from_page_id=self.instagram_data.sender_id,
            to_page_id=self.user_page_data.facebook_page_id,
            user_id=self.user_page_data.user_id,
        )

    def update_databoard(self):
        now = datetime.now()
        databoard = services.databoard.live_comment_stat.get(
            self.db,
            facebook_page_id=self.user_page_data.facebook_page_id,
            now=now
        )

        if not databoard:
            databoard = services.databoard.live_comment_stat.create(
                self.db,
                facebook_page_id=self.user_page_data.facebook_page_id,
                count=1,
                now=now,
            )
        else:
            services.databoard.live_comment_stat.update_count(
                self.db,
                db_obj=databoard,
                added_count=1
            )

        return databoard
