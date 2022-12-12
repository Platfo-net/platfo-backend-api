from app.core.config import settings
from fastapi.testclient import TestClient
from tests.utils.user import get_user_token_headers


def test_get_own_user(client: TestClient) -> None:
    headers = get_user_token_headers(client)
    r = client.get(f"{settings.API_V1_STR}/user/me", headers=headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["email"] == settings.FIRST_USER_EMAIL


def test_register_user(client: TestClient) -> None:
    user_email = "test_duplicate@example.com"
    user_password = "Test@123456"
    r = client.post(
        f"{settings.API_V1_STR}/user/register",
        json={"email": user_email, "password": user_password},
    )

    assert r.status_code == 201
