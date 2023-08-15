from app import models
from app.services.databoard.databoard_base import DataboardBase


class LeadMessageStatServices(DataboardBase):
    pass


lead_message_stat = LeadMessageStatServices(models.databoard.LeadMessageStat)
