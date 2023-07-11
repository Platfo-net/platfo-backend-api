from app import models
from app.services.databoard.databoard_base import DataboardBase


class ContactStatServices(DataboardBase):
    pass


contact_stat = ContactStatServices(models.databoard.ContactStat)
