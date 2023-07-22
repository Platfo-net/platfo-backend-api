
from abc import abstractmethod
from datetime import datetime
from typing import List

from redis import Redis
from sqlalchemy.orm import Session

from app import schemas, services
from app.constants.impression import Impression
from app.constants.message_direction import MessageDirection
from app.constants.widget_type import WidgetType
from app.core.instagram.instagram import (InstagramData, SavedMessage,
                                          UserData)
from app.core.instagram.graph_api import graph_api


def convert_message(content):
    if type(content) == str:
        return content
    if message := content.get("message"):
        return message
    if message := content.get("text"):
        return message
    if message := content.get("question"):
        return message
    if message := content.get("title"):
        return message
    return ""


class BaseHandler:
    def __init__(
            self,
            instagram_data: InstagramData,
            user_page_data: UserData,
            redis_client: Redis,
            db: Session
    ):
        self.redis_client = redis_client
        self.db = db
        self.instagram_data = instagram_data
        self.user_page_data = user_page_data

    def __call__(self):
        pass

    @abstractmethod
    def pack(self):
        raise NotImplementedError

    def save_comment(
        self,
        from_page_id: int = None,
        to_page_id: int = None,
        user_id: int = None,
    ):
        contact = services.live_chat.contact.get_contact_by_igs_id(
            self.db, contact_igs_id=from_page_id
        )
        if not contact:
            contact_in = schemas.live_chat.ContactCreate(
                contact_igs_id=from_page_id,
                user_page_id=to_page_id,
                user_id=user_id,
                first_impression=Impression.COMMENT,
                last_interaction_at=datetime.fromtimestamp(float(self.instagram_data.entry_time))
            )
            services.live_chat.contact.create(self.db, obj_in=contact_in)

            information = {
                'username': '',
                'profile_image': '',
                'name': '',
                'followers_count': 0,
                'is_verified_user': True,
                'is_user_follow_business': True,
                'is_business_follow_user': False,
            }
            contact = services.live_chat.contact.set_information(
                self.db,
                contact_igs_id=from_page_id,
                information=information,
            )
        else:
            services.live_chat.contact.update_interactions(
                self.db,
                contact_igs_id=contact.contact_igs_id,
                last_interaction_at=datetime.fromtimestamp(float(self.instagram_data.entry_time))
            )
        return 0

    @abstractmethod
    def update_databoard(self):
        raise NotImplementedError

    def save_message(self, message: SavedMessage):
        is_new = False
        # set and convert message time
        if self.instagram_data.timestamp:
            time = datetime.fromtimestamp(self.instagram_data.timestamp / 1000.0)
        elif self.instagram_data.entry_time:
            time = datetime.fromtimestamp(self.instagram_data.entry_time / 1000.0)
        else:
            time = datetime.now()

        if message.direction == MessageDirection.IN:
            contact = services.live_chat.contact.get_contact_by_igs_id(
                self.db, contact_igs_id=message.from_page_id
            )
            if not contact:
                contact_in = schemas.live_chat.ContactCreate(
                    contact_igs_id=message.from_page_id,
                    facebook_page_id=message.to_page_id,
                    user_id=message.user_id,
                    first_impression=Impression.MESSAGE,
                    last_message=convert_message(message.content),
                    last_message_at=time,
                    last_interaction_at=time,
                )
                new_contact = services.live_chat.contact.create(self.db, obj_in=contact_in)

                information = graph_api.get_contact_information_from_facebook(
                    contact_igs_id=new_contact.contact_igs_id,
                    page_access_token=self.user_page_data.facebook_page_token,
                )
                services.live_chat.contact.set_information(
                    self.db,
                    contact_igs_id=message.from_page_id,
                    information=information,
                )
                is_new = True
            else:
                services.live_chat.contact.update_interactions(
                    self.db,
                    contact_igs_id=message.from_page_id,
                    last_message=convert_message(message.content),  # TODO Handle this to be as str
                    last_message_at=time,
                    last_interaction_at=time,

                )

        if message.timestamp:
            time = datetime.fromtimestamp(message.timestamp / 1000.0)
        else:
            time = datetime.now()
        report = services.live_chat.message.create(
            self.db,
            obj_in=schemas.live_chat.MessageCreate(
                from_page_id=message.from_page_id,
                to_page_id=message.to_page_id,
                content=message.content,
                mid=message.mid,
                user_id=message.user_id,
                direction=message.direction,
                datetime=time,
            ),
        )
        return report, is_new


class BotBaseHandler(BaseHandler):
    def check_connection_and_get_detail(self, trigger, application):
        _, detail = services.connection.get_connection(
            self.db,
            account_id=self.user_page_data.account_id,
            application_name=application,
            trigger=trigger
        )

        return detail

    def send_widget(
        self,
        widget: dict,
        quick_replies: List[dict],
        contact_igs_id: int,
        chatflow_id: int=None,
    ):

        while widget["widget_type"] in (WidgetType.TEXT, WidgetType.MEDIA):
            mid = None
            if widget["widget_type"] == WidgetType.MEDIA:
                mid = self.handle_media(widget, contact_igs_id)

            if widget["widget_type"] == WidgetType.TEXT:
                mid = self.handle_text(widget, contact_igs_id, quick_replies)

            saved_message = self.pack_our_message(contact_igs_id, widget, mid)
            self.save_message(
                saved_message
            )

            payload = widget["uuid"]

            node = services.bot_builder.node.get_next_node(self.db, from_id=payload)

            if node is None:
                break

            widget = node.widget
            quick_replies = node.quick_replies

        if widget["widget_type"] == "MENU":
            mid = self.handle_menu(widget, chatflow_id, quick_replies, contact_igs_id)
            self.pack_our_message(contact_igs_id, widget, mid)
            saved_message = self.save_message(saved_message)

        return widget

    def handle_media(self, widget, contact_igs_id: int) -> str:
        mid = graph_api.send_media(
            widget["title"],
            widget["image"],
            from_id=self.user_page_data.facebook_page_id,
            to_id=contact_igs_id,
            page_access_token=self.user_page_data.facebook_page_token,
        )
        return mid

    def handle_text(self, widget, contact_igs_id: int, quick_replies) -> str:
        mid = graph_api.send_text_message(
            text=widget["message"],
            from_id=self.user_page_data.facebook_page_id,
            to_id=contact_igs_id,
            page_access_token=self.user_page_data.facebook_page_token,
            quick_replies=quick_replies,
        )
        return mid

    def handle_menu(self, widget, chatflow_id, quick_replies, contact_igs_id: int):
        mid = graph_api.send_menu(
            data = widget,
            quick_replies=quick_replies,
            from_id=self.user_page_data.facebook_page_id,
            to_id=contact_igs_id,
            chatflow_id=chatflow_id,
            page_access_token=self.user_page_data.facebook_page_token,
        )
        return mid

    def pack_our_message(self, contact_igs_id: int, content, mid) -> SavedMessage:
        saved_message = SavedMessage(
            from_page_id=self.user_page_data.facebook_page_id,
            to_page_id=contact_igs_id,
            mid=mid,
            content=content,
            user_id=self.user_page_data.user_id,
            direction=MessageDirection.OUT
        )
        return saved_message
