

from app.core.bot_builder.handlers.base import BaseHandler


class LiveCommentHandler(BaseHandler):
    def __call__(self):
        self.save_comment(
            db=self.db,
            from_page_id=self.instagram_data.sender_id,
            to_page_id=self.user_page_data.facebook_page_id,
            user_id=self.user_page_data.user_id,
        )
