from app.core.config import settings
from fastapi.testclient import TestClient
# from tests.utils.user import get_user_token_headers


def test_register_user(client: TestClient) -> None:
    client.post(
        f"{settings.API_V1_STR}/user/register",
        json={"email": None, "password": None},
    )
