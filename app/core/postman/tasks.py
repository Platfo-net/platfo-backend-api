
from app.core.celery import celery
from app import services
from app.db.session import SessionLocal
from app.constants.campaign_status import CampaignStatus
from app.core.bot_builder.instagram_graph_api import graph_api
from app.core.bot_builder.extra_classes import UserData
from app.constants.widget_type import WidgetType


@celery.task
def campaign_terminal():
    db = SessionLocal()
    campaigns = services.postman.campaign.get_active_campaigns(db)

    if len(campaigns) == 0:
        return 0

    for campaign in campaigns:
        campaign_handler.delay(campaign.id)


@celery.task
def campaign_handler(campaign_id):
    db = SessionLocal()
    campaign = services.postman.campaign.get(db, campaign_id)
    campaign_contacts = services.postman.campaign_contact.get_campaign_unsend_contacts(
        db, campaign_id=campaign_id, count=150)
    services.postman.campaign.change_activity(
        db, campaign_id=campaign_id, is_active=True)

    content = campaign.content

    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=campaign.facebook_page_id)

    instagram_page = UserData(
        user_id=instagram_page.user_id,
        facebook_page_token=instagram_page.facebook_page_token,
        facebook_page_id=instagram_page.facebook_page_id,
        account_id=instagram_page.id
    )

    for contact in campaign_contacts:
        if content.widget_type == WidgetType.TEXT:
            mid = graph_api.send_text_message(
                text=content.text,
                from_id=instagram_page.facebook_page_id,
                to_id=contact.instagram_igs_id,
                page_access_token=instagram_page.facebook_page_token
            )
            # to do

        if content.widget_type == WidgetType.MENU:
            mid = graph_api.send_menu(
                data=content,
                quick_replies=[],
                from_id=instagram_page.facebook_page_id,
                to_id=contact.instagram_igs_id,
                page_access_token=instagram_page.facebook_page_token
            )
            # TODO

    # result handling
    all_count = services.postman.campaign_contacts.get_all_contacts_count(
        db, campaign_id=campaign_id)
    send_count = services.postman.campaign_contacts.get_campaign_unsend_contacts_count(
        db, campaign_id=campaign_id)

    if all_count == send_count:
        services.postman.campaign.change_status(
            db, campaign_id=campaign.id, status=CampaignStatus.DONE)
