from sqlalchemy.orm import Session

from app import models, schemas, services
from .fixtures import sample_instagram_page  # noqa


def test_create_instagram_page(db: Session, sample_instagram_page: models.InstagramPage):  # noqa
    assert sample_instagram_page is not None


def test_update_instagram_page(db: Session, sample_instagram_page: models.InstagramPage):  # noqa
    updated_page = schemas.InstagramPageUpdate(
        username="sample_updated_username",
    )  # noqa
    page = services.instagram_page.update(
        db,
        db_obj=sample_instagram_page,
        obj_in=updated_page,
    )

    assert page is not None
    assert isinstance(page, models.InstagramPage)


def test_delete_instagram_page(db: Session, sample_instagram_page: models.InstagramPage):  # noqa
    services.instagram_page.remove(db, id=sample_instagram_page.id)
    page = services.instagram_page.get(db, sample_instagram_page.id)
    assert page is None


def test_get_page_by_facebook_page_id(db: Session, sample_instagram_page: models.InstagramPage):  # noqa
    page = services.instagram_page.get_by_facebook_page_id(
        db,
        facebook_page_id=sample_instagram_page.facebook_page_id
    )
    assert isinstance(page, models.InstagramPage)
    assert page == sample_instagram_page


def test_get_user_pages(db, sample_instagram_page: models.InstagramPage): # noqa
    page_in = schemas.InstagramPageCreate(
        biography="sample biography",
        facebook_page_id=12345689,
        instagram_page_id=12346789,
        username="sample_username",
        profile_picture_url="sample_profile_picture.facebook.com",
        facebook_user_long_lived_token="quwidsfsjdfsdjfs",
        facebook_user_id="456",
        name="sample_name",
        website="sample_website.com",
        ig_id="47854",
        followers_count=1,
        follows_count=1,
        user_id=sample_instagram_page.user_id,
    )
    services.instagram_page.create(db, obj_in=page_in)

    pages = services.instagram_page.get_multi_by_user_id(db, user_id=sample_instagram_page.user_id)

    assert len(pages) == 2


def test_get_by_page_id(db, sample_instagram_page: models.InstagramPage):  # noqa
    page = services.instagram_page.get_by_instagram_page_id(
        db, instagram_page_id=sample_instagram_page.instagram_page_id)

    assert page is not None
    assert page == sample_instagram_page
