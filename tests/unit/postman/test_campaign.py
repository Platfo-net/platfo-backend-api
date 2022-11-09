from sqlalchemy.orm import Session
from app import services, schemas, models
from app.core.config import settings
from tests.unit.postman import helper
from app.constants.campaign_status import CampaignStatus
from app.constants.widget_type import WidgetType


def test_create_campaign(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="12")

    campaign = helper.create_campaign(db, user.id, account.facebook_page_id)
    assert isinstance(campaign, models.postman.Campaign)
    assert campaign.content is None
    assert campaign.user_id == user.id
    assert campaign.facebook_page_id == "12"
    assert campaign.is_draft is True
    assert campaign.status == CampaignStatus.PENDING


def test_update_campaign_information(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="13")

    db_obj = helper.create_campaign(db, user.id, account.facebook_page_id)

    content = {"title": "test", "widget_type": WidgetType.TEXT}
    obj_in = schemas.postman.CampaignUpdate(
        name="test_campaign_updated",
        description="test_campaign_description_updated",
        content=content,
        is_draft=False,
    )

    campaign = services.postman.campaign.update(
            db,
            user_id=user.id,
            db_obj=db_obj,
            obj_in=obj_in
    )
    assert isinstance(campaign, models.postman.Campaign)
    assert campaign.name == "test_campaign_updated"
    assert campaign.description == "test_campaign_description_updated"
    assert campaign.is_draft is False
    assert campaign.content == content


def test_change_campaign_status(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="14")

    campaign = helper.create_campaign(db, user.id, account.facebook_page_id)

    services.postman.campaign.change_status(
        db, campaign_id=campaign.id, status=CampaignStatus.DONE)

    new_campaign = services.postman.campaign.get(db=db, campaign_id=campaign.id)

    assert new_campaign.status == CampaignStatus.DONE


def test_change_campaign_is_draft(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="15")

    campaign = helper.create_campaign(db, user.id, account.facebook_page_id)

    services.postman.campaign.change_is_draft(db, campaign_id=campaign.id, is_draft=True)

    new_campaign = services.postman.campaign.get(db=db, campaign_id=campaign.id)

    assert new_campaign.is_draft is True


def test_change_campaign_activity(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="15")

    campaign = helper.create_campaign(db, user.id, account.facebook_page_id)

    services.postman.campaign.change_activity(
        db, campaign_id=campaign.id, is_active=True)

    campaign = services.postman.campaign.get(db=db, campaign_id=campaign.id)

    assert campaign.is_active is True

    services.postman.campaign.change_activity(
        db, campaign_id=campaign.id, is_active=False)

    campaign = services.postman.campaign.get(db=db, campaign_id=campaign.id)

    assert campaign.is_active is False
