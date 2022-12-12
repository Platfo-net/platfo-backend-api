from typing import Dict
from app.core.config import settings
from fastapi.testclient import TestClient


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"email": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/auth/access-token", json=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def get_admin_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "email": settings.FIRST_ADMIN_EMAIL,
        "password": settings.FIRST_ADMIN_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/access-token", json=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_user_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "email": settings.FIRST_USER_EMAIL,
        "password": settings.FIRST_USER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/access-token", json=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
