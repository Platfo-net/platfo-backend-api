from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import services, schemas
from app.core.config import settings
from tests.unit.postman import helper
from tests.utils.user import get_user_token_headers


def test_create_group(client: TestClient, db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(
        db, facebook_page_id=settings.SAMPLE_FACEBOOK_PAGE_ID
    )
    contact_1 = services.live_chat.contact.create(
        db,
        obj_in=schemas.live_chat.ContactCreate(
            user_page_id=account.facebook_page_id,
            user_id=user.id,
            contact_igs_id=settings.SAMPLE_CONTACT_IGS_ID,
        ),
    )
    headers = get_user_token_headers(client)

    name = "group_test"
    description = "this is a description"
    facebook_page_id = contact_1.user_page_id
    contacts = [
        {"contact_igs_id": contact_1.contact_igs_id, "contact_id": str(contact_1.id)}
    ]
    r = client.post(
        f"{settings.API_V1_STR}/postman/group/",
        json={
            "name": name,
            "description": description,
            "facebook_page_id": facebook_page_id,
            "contacts": contacts,
        },
        headers=headers,
    )
    json_response = r.json()
    assert r.status_code == 200
    assert json_response["name"] == name


def test_get_groups(client: TestClient, db: Session):
    headers = get_user_token_headers(client)
    facebook_page_id = settings.SAMPLE_FACEBOOK_PAGE_ID

    r = client.get(
        f"{settings.API_V1_STR}/postman/group/{facebook_page_id}", headers=headers
    )
    json_response = r.json()
    assert r.status_code == 200
    assert len(json_response["items"]) >= 1
    assert json_response["items"][0]["name"] == "group_test"
    assert json_response["pagination"]


def test_delete_group(client: TestClient, db: Session):
    headers = get_user_token_headers(client)
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="4")
    group = helper.create_group(db, user.id, account.facebook_page_id)

    r = client.delete(
        f"{settings.API_V1_STR}/postman/group/{group.id}", headers=headers
    )

    assert r.status_code == 200
    assert r.json() is None
