from app import models
from app.services.databoard.databoard_base import DataboardBase


class LiveCommentStatServices(DataboardBase):
    pass


live_comment_stat = LiveCommentStatServices(models.databoard.LiveCommentStat)
