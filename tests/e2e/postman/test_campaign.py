from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import services
from app.core.config import settings
from tests.unit.postman import helper
from tests.utils.user import get_user_token_headers


def test_create_campaign(client: TestClient, db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="1")
    group = helper.create_group(db, user.id, account.facebook_page_id)
    headers = get_user_token_headers(client)

    name = "campaign_test"
    description = "this is a description for campaign"
    facebook_page_id = account.facebook_page_id
    group_id = group.id
    is_draft = True
    content = dict(
        title="pm",
        widget_type="MENU",
        type="WEB_URL",
        choices=[{"text": "hello this is test!", "url": "test.com"}],
    )

    r = client.post(
        f"{settings.API_V1_STR}/postman/campaign/",
        json={
            "name": name,
            "description": description,
            "facebook_page_id": facebook_page_id,
            "group_id": str(group_id),
            "is_draft": is_draft,
            "content": content,
        },
        headers=headers,
    )
    json_response = r.json()
    assert r.status_code == 200
    assert json_response["status"]
    assert json_response["group_name"] == group.name


def test_get_campaigns(client: TestClient, db: Session):
    headers = get_user_token_headers(client)

    r = client.get(f"{settings.API_V1_STR}/postman/campaign/all", headers=headers)
    json_response = r.json()
    assert r.status_code == 200
    assert len(json_response["items"]) >= 1
    assert json_response["items"][0]["name"] == "campaign_test"
    assert json_response["pagination"]


def test_get_campaign_detail(client: TestClient, db: Session):
    headers = get_user_token_headers(client)
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="2")
    campaign = helper.create_campaign(db, user.id, account.facebook_page_id)

    r = client.get(
        f"{settings.API_V1_STR}/postman/campaign/{campaign.id}", headers=headers
    )
    json_response = r.json()
    assert r.status_code == 200
    assert json_response["user_id"] == str(user.id)
    assert json_response["group_name"] == campaign.group_name
    assert json_response["account"]
    assert json_response["id"] == str(campaign.id)
