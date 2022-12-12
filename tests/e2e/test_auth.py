from app.core.config import settings
from fastapi.testclient import TestClient


def test_get_access_token(client: TestClient):
    login_data = {
        "email": settings.FIRST_USER_EMAIL,
        "password": settings.FIRST_USER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/access-token", json=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_login_failure(client: TestClient):
    login_data = {
        "email": "testwrongemail@example.com",
        "password": "123456789",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/access-token", json=login_data)
    assert r.status_code == 401
