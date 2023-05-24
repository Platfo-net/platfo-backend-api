from celery import shared_task

from app import services
from app.constants.campaign_status import CampaignStatus
from app.constants.message_direction import MessageDirection
from app.core import storage, utils
from app.core.bot_builder.extra_classes import SavedMessage, UserData
from app.core.bot_builder.instagram_graph_api import graph_api
from app.core.config import settings
from app.db.session import SessionLocal


@shared_task
def campaign_terminal():
    db = SessionLocal()
    campaigns = services.notifier.campaign.get_active_campaigns(db)

    if len(campaigns) == 0:
        db.close()
        return 0

    for campaign in campaigns:
        unsend_count = (
            services.notifier.campaign_contact.get_campaign_unsend_contacts_count(
                db, campaign_id=campaign.id
            )
        )
        if unsend_count == 0:
            services.notifier.campaign.change_status(
                db, campaign_id=campaign.id, status=CampaignStatus.DONE
            )
        else:
            campaign_handler.delay(campaign.id)
    db.close()
    return 0


@shared_task
def campaign_handler(campaign_id):
    db = SessionLocal()
    campaign = services.notifier.campaign.get(db=db, campaign_id=campaign_id)
    campaign_contacts = services.notifier.campaign_contact.get_campaign_unsend_contacts(
        db, campaign_id=campaign_id, count=settings.CAMPAIGN_INTERVAL_SEND_CONTACT_COUNT
    )

    services.notifier.campaign.change_activity(
        db, campaign_id=campaign_id, is_active=True
    )

    campaign_text = campaign.content.get('text', None)
    if not campaign_text:
        return None
    campaign_image = campaign.image
    campaign_image_url = None
    if campaign_image:
        campaign_image_url = storage.get_file(
            campaign_image, settings.S3_CAMPAIGN_BUCKET
        ).url

    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=campaign.facebook_page_id
    )

    instagram_page = UserData(
        user_id=instagram_page.user_id,
        facebook_page_token=instagram_page.facebook_page_token,
        facebook_page_id=instagram_page.facebook_page_id,
        account_id=instagram_page.id,
    )
    sent_contacts = []

    for contact in campaign_contacts:
        mid = None
        for _ in range(3):
            if campaign_image_url:
                mid = graph_api.send_media(
                    text=campaign_text,
                    image_url=campaign_image_url,
                    from_id=instagram_page.facebook_page_id,
                    to_id=contact.contact_igs_id,
                    page_access_token=instagram_page.facebook_page_token,
                )
            else:
                mid = graph_api.send_text_message(
                    text=campaign_text,
                    from_id=instagram_page.facebook_page_id,
                    to_id=contact.contact_igs_id,
                    page_access_token=instagram_page.facebook_page_token,
                    quick_replies=[],
                )
            if mid:
                break

        if mid:
            contact.mid = mid
            sent_contacts.append(contact)
            saved_message = SavedMessage(
                from_page_id=instagram_page.facebook_page_id,
                to_page_id=contact.contact_igs_id,
                mid=mid,
                content={'text': campaign_text},
                user_id=instagram_page.user_id,
                direction=MessageDirection.OUT,
            )
            utils.save_message(db, saved_message)

    services.notifier.campaign_contact.change_send_status_bulk(
        db=db, campaign_contacts_in=sent_contacts, is_sent=True
    )

    services.notifier.campaign.change_activity(
        db, campaign_id=campaign_id, is_active=False
    )
    db.close()
    return 0
