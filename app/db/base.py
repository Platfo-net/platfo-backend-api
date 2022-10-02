# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.role import Role  # noqa
from app.models.user import User  # noqa
from app.models.instagram_page import InstagramPage  # noqa
from app.models.connection import Connection  # noqa

from app.models.bot_builder.chatflow import Chatflow  # noqa
from app.models.bot_builder.node import Node  # noqa

from app.models.live_chat.contact import Contact  # noqa
from app.models.live_chat.message import Message  # noqa

from app.models.notification import Notification, NotificationUser  # noqa


from app.models.academy import Category, Content,\
      ContentCategory, Label, ContentLabel  # noqa


from app.models.bot_builder.node_ui import NodeUI  # noqa
from app.models.bot_builder.edge import Edge  # noqa
