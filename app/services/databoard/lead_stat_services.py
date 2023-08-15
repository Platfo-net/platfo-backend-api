from app import models
from app.services.databoard.databoard_base import DataboardBase


class LeadStatServices(DataboardBase):
    pass


lead_stat = LeadStatServices(models.databoard.LeadStat)
