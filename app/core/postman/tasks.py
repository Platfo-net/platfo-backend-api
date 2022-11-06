
from typing import Any
from app.constants.message_direction import MessageDirection
from app import schemas, services
from app.db.session import SessionLocal
from app.constants.campaign_status import CampaignStatus
from app.core.bot_builder.instagram_graph_api import graph_api
from app.core.bot_builder.extra_classes import UserData
from app.constants.widget_type import WidgetType
from celery import shared_task


@shared_task
def save_message(
    from_page_id: str = None,
    to_page_id: str = None,
    mid: str = None,
    content: dict = None,
    user_id: Any = None,
):

    db = SessionLocal()
    services.live_chat.contact.update_last_message(
        db, contact_igs_id=to_page_id, last_message=content
    )

    report = services.live_chat.message.create(
        db,
        obj_in=schemas.live_chat.MessageCreate(
            from_page_id=from_page_id,
            to_page_id=to_page_id,
            content=content,
            mid=mid,
            user_id=user_id,
            direction=MessageDirection.OUT["name"],
        ),
    )
    return report


@shared_task
def campaign_terminal():
    db = SessionLocal()
    campaigns = services.postman.campaign.get_active_campaigns(db)
    print('campaignsssssss', campaigns)

    if len(campaigns) == 0:
        return 0

    for campaign in campaigns:
        unsend_count = services.postman.campaign_contact.\
            get_campaign_unsend_contacts_count(
                db, campaign_id=campaign.id
            )
        print('unsend_counttttttt', unsend_count)

        if unsend_count == 0:
            services.postman.campaign.change_status(
                db, campaign_id=campaign.id, status=CampaignStatus.DONE)
        else:
            campaign_handler.delay(campaign.id)
    return 0


@shared_task
def campaign_handler(campaign_id):
    from app.core.config import settings
    db = SessionLocal()
    campaign = services.postman.campaign.get(db=db, campaign_id=campaign_id)
    print('campaign isssssss', campaign)
    campaign_contacts = services.postman.campaign_contact.get_campaign_unsend_contacts(
        db, campaign_id=campaign_id, count=settings.CAMPAIGN_INTERVAL_SEND_CONTACT_COUNT)
    print('campaign_contacts isssssss', campaign_contacts)

    services.postman.campaign.change_activity(
        db, campaign_id=campaign_id, is_active=True)

    content = campaign.content
    print('content issssssss', content)

    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=campaign.facebook_page_id)
    print('instagram_page issssssssssss 111111111111111111', instagram_page)

    instagram_page = UserData(
        user_id=instagram_page.user_id,
        facebook_page_token=instagram_page.facebook_page_token,
        facebook_page_id=instagram_page.facebook_page_id,
        account_id=instagram_page.id
    )
    print('instagram_page issssssssssss 2222222222222222', instagram_page)
    sent_contacts = []
    for contact in campaign_contacts:
        print('omd to foooooooooorrrrrrrrrrrr')
        mid = None
        if content["widget_type"] == WidgetType.TEXT["name"]:
            for _ in range(3):
                mid = graph_api.send_text_message(
                    text=content["text"],
                    from_id=instagram_page.facebook_page_id,
                    to_id=contact.contact_igs_id,
                    page_access_token=instagram_page.facebook_page_token,
                    quick_replies=[]
                )
                if mid:
                    break

        if content["widget_type"] == WidgetType.MENU["name"]:
            print('omd to sharte menuuuuuuuuuuuuuuuuuu')
            for _ in range(3):
                mid = graph_api.send_menu(
                    data=content,
                    from_id=instagram_page.facebook_page_id,
                    to_id=contact.contact_igs_id,
                    page_access_token=instagram_page.facebook_page_token
                )
                if mid:
                    break
        if mid:
            contact.mid = mid
            sent_contacts.append(contact)
            save_message(
                from_page_id=instagram_page.facebook_page_id,
                to_page_id=contact.contact_igs_id,
                mid=mid,
                content=content,
                user_id=instagram_page.user_id,
            )
    services.postman.campaign_contact.change_send_status_bulk(
        db=db, campaign_contacts_in=sent_contacts, is_sent=True)
    print('residdddddddeeeeeeeee yeki ba akharrrrrrrr')
    services.postman.campaign.change_activity(
        db, campaign_id=campaign_id, is_active=False)

    return 0
