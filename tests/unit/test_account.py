from app import services, schemas, models
from sqlalchemy.orm import Session
import uuid
from app.core.config import settings


def test_create_instagram_page(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    facebook_page_id = "1587469857425621"
    facebook_page_token = str(uuid.uuid4())
    instagram_page_id = "5789427569321078"
    instagram_page_in = schemas.InstagramPageCreate(
        user_id=user.id,
        facebook_page_id=facebook_page_id,
        facebook_page_token=facebook_page_token,
        instagram_page_id=instagram_page_id,
        username="test",
    )
    instagram_page = services.instagram_page.create(db, obj_in=instagram_page_in)

    assert isinstance(instagram_page, models.InstagramPage)
    assert instagram_page.user_id == user.id
    assert instagram_page.facebook_page_id == facebook_page_id
    assert instagram_page.instagram_page_id == instagram_page_id
    assert instagram_page.facebook_page_token == facebook_page_token


def test_get_instagram_page(db: Session):
    user = services.user.register(
        db, obj_in=schemas.UserRegister(email="test@example.com", password="test@123")
    )
    facebook_page_id = "9787469857425621"
    facebook_page_token = "testtoken"
    instagram_page_id = "1289427569321078"
    instagram_page_in = schemas.InstagramPageCreate(
        user_id=user.id,
        facebook_page_id=facebook_page_id,
        facebook_page_token=facebook_page_token,
        instagram_page_id=instagram_page_id,
        username="test",
    )
    instagram_page = services.instagram_page.create(db, obj_in=instagram_page_in)

    instagram_page_1 = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=facebook_page_id
    )
    instagram_page_2 = services.instagram_page.get_by_instagram_page_id(
        db, instagram_page_id=instagram_page_id
    )
    instagram_page_3 = services.instagram_page.get(db, instagram_page.id)
    user_instagram_pages = services.instagram_page.get_multi_by_user_id(
        db, user_id=user.id
    )

    assert isinstance(instagram_page_1, models.InstagramPage)
    assert isinstance(instagram_page_2, models.InstagramPage)
    assert isinstance(instagram_page_3, models.InstagramPage)

    assert instagram_page_1.facebook_page_id == facebook_page_id
    assert instagram_page_2.facebook_page_id == facebook_page_id
    assert instagram_page_3.facebook_page_id == facebook_page_id
    assert instagram_page_1.instagram_page_id == instagram_page_id
    assert instagram_page_2.instagram_page_id == instagram_page_id
    assert instagram_page_3.instagram_page_id == instagram_page_id
    assert instagram_page_1.facebook_page_token == facebook_page_token
    assert instagram_page_2.facebook_page_token == facebook_page_token
    assert instagram_page_3.facebook_page_token == facebook_page_token
    assert len(user_instagram_pages) == 1

    assert isinstance(user_instagram_pages[0], models.InstagramPage)
