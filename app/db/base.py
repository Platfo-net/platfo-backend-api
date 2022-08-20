# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.role import Role  # noqa
from app.models.user import User  # noqa
from app.models.facebook_account import FacebookAccount  # noqa
from app.models.instagram_page import InstagramPage  # noqa
from app.models.credit import Credit  # noqa
from app.models.plan import Plan  # noqa
from app.models.connection import Connection  # noqa
from app.models.trigger import Trigger  # noqa
from app.models.connection_chatflow import ConnectionChatflow  # noqa
from app.models.chatflow import Chatflow  # noqa
from app.models.node import Node  # noqa

