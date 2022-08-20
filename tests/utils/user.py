from typing import Dict

from app import services , schemas
from app.core.config import settings
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

regular_user_email = "tester@email.com"
regular_user_password = "supersecretpassword"
regular_user_full_name = "john doe"


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"email": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/auth/access-token", json=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def get_superadmin_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "email": settings.FIRST_ADMIN_EMAIL,
        "password": settings.FIRST_ADMIN_PASSWORD,
    }
    r = client.post(
        f"{settings.API_V1_STR}/auth/access-token", json=login_data
    )
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def authentication_token_from_email(
    *, client: TestClient, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    user = services.user.get_by_email(db, email=regular_user_email)
    if not user:
        user_in = schemas.UserRegister(
            email=regular_user_email,
            password=regular_user_password,
        )
        services.user.register(db, obj_in=user_in)
    return user_authentication_headers(
        client=client, 
        email=regular_user_email, 
        password=regular_user_password
    )
