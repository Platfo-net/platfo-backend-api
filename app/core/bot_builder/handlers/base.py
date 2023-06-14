
from abc import abstractmethod

from redis import Redis
from sqlalchemy.orm import Session

from app import schemas, services
from app.constants.impression import Impression
from app.constants.message_direction import MessageDirection
from app.core.bot_builder.extra_classes import (InstagramData, SavedMessage,
                                                UserData)
from app.core.bot_builder.instagram_graph_api import graph_api


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
                comment_count=1,
                first_impression=Impression.COMMENT,
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
            services.live_chat.contact.set_information(
                self.db,
                contact_igs_id=from_page_id,
                information=information,
            )
            return 0

        services.live_chat.contact.update_last_comment_count(
            self.db, contact_igs_id=contact.contact_igs_id
        )
        return 0

    def save_message(self, message: SavedMessage):
        if message.direction == MessageDirection.IN:
            contact = services.live_chat.contact.get_contact_by_igs_id(
                self.db, contact_igs_id=message.from_page_id
            )
            if not contact:
                contact_in = schemas.live_chat.ContactCreate(
                    contact_igs_id=message.from_page_id,
                    user_page_id=message.to_page_id,
                    user_id=message.user_id,
                    message_count=1,
                    first_impression=Impression.MESSAGE,
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
            else:
                services.live_chat.contact.update_last_message_count(
                    self.db, contact_igs_id=message.from_page_id
                )

        if message.direction == MessageDirection.IN:
            services.live_chat.contact.update_last_message(
                self.db, contact_igs_id=message.from_page_id, last_message=str(message.content)
            )

        else:
            services.live_chat.contact.update_last_message(
                self.db, contact_igs_id=message.to_page_id, last_message=str(message.content)
            )

        report = services.live_chat.message.create(
            self.db,
            obj_in=schemas.live_chat.MessageCreate(
                from_page_id=message.from_page_id,
                to_page_id=message.to_page_id,
                content=message.content,
                mid=message.mid,
                user_id=message.user_id,
                direction=message.direction,
            ),
        )
        return report
