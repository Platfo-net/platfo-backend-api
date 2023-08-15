

from app import services
from app.core.instagram.handlers import BaseHandler


class MessageSeenHandler(BaseHandler):
    def __call__(self):
        services.notifier.campaign_lead.seen_message(self.db, mid=self.instagram_data.mid)
