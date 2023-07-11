from app import models
from app.services.databoard.databoard_base import DataboardBase


class ContactMessageStatServices(DataboardBase):
    pass


contact_message_stat = ContactMessageStatServices(models.databoard.ContactMessageStat)
