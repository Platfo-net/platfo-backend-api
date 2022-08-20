from typing import Dict
from app import services , schemas
from app.core.config import settings
from fastapi.testclient import TestClient
from tests.utils.user import regular_user_email , regular_user_password
from sqlalchemy.orm import Session

def test_get_access_token(client: TestClient , db:Session) -> None:
    login_data = {
        "email": regular_user_email,
        "password": regular_user_password,
    }
    r = client.post(
        f"{settings.API_V1_STR}/auth/access-token", json=login_data
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
