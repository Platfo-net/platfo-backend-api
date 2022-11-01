
from sqlalchemy.orm import Session
from app import services, schemas
from app.core.config import settings
import uuid


def create_instagram_account(db: Session, page_id):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    facebook_page_id = page_id
    facebook_page_token = str(uuid.uuid4())
    instagram_page_id = "5789427549321078"
    instagram_page_in = schemas.InstagramPageCreate(
        user_id=user.id,
        facebook_page_id=facebook_page_id,
        facebook_page_token=facebook_page_token,
        instagram_page_id=instagram_page_id,
        username="test",
    )
    instagram_page = services.instagram_page.create(
        db, obj_in=instagram_page_in)

    return instagram_page


def create_campaign(db: Session, user_id, facebook_page_id):
    campaign_in = schemas.postman.CampaignCreate(
        name="test_campaign",
        description="test_campaign_description",
        facebook_page_id=facebook_page_id,
    )
    return services.postman.campaign.create(db, obj_in=campaign_in, user_id=user_id)
